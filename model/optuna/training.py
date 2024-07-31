# Custom Token Classification Training Script
import evaluate
import numpy as np
import optuna
import yaml
import wandb
import os
from datasets import load_dataset, load_metric
from transformers import (
    Trainer, 
    AutoTokenizer, 
    TrainingArguments, 
    AutoModelForTokenClassification, 
    DataCollatorForTokenClassification,
)
os.environ["WANDB_START_METHOD"] = "thread"

# Config
with open('config.yaml') as file:
    config = yaml.safe_load(file)

model_args = config['model_args']
training_args = config['training_args']
data_args = config['data_args']
wandb_args = config['wandb']

# Get the Dataset
raw_dataset = load_dataset(data_args['dataset_name']) # download from the Hub
ner_feature = raw_dataset["train"].features["ner_tags"]
label_names = ner_feature.feature.names

model_checkpoint = "bert-base-cased"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

def align_labels_with_tokens(labels, word_ids):
    new_labels = []
    current_word = None
    for word_id in word_ids:
        if word_id != current_word:
            # Start of a new word!
            current_word = word_id
            label = -100 if word_id is None else labels[word_id]
            new_labels.append(label)
        elif word_id is None:
            # Special token
            new_labels.append(-100)
        else:
            # Same word as previous token
            label = labels[word_id]
            # If the label is B-XXX we change it to I-XXX
            if label % 2 == 1:
                label += 1
            new_labels.append(label)

    return new_labels

def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["tokens"], truncation=True, is_split_into_words=True
    )
    all_labels = examples["ner_tags"]
    new_labels = []
    for i, labels in enumerate(all_labels):
        word_ids = tokenized_inputs.word_ids(i)
        new_labels.append(align_labels_with_tokens(labels, word_ids))

    tokenized_inputs["labels"] = new_labels
    return tokenized_inputs

tokenized_datasets = raw_dataset.map(
    tokenize_and_align_labels,
    batched=True,
    remove_columns=raw_dataset["train"].column_names,
)

# Data Collation
data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

# Metrics
metric = evaluate.load("seqeval")
def compute_metrics(eval_preds):
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)

    # Remove ignored index (special tokens) and convert to labels
    true_labels = [[label_names[l] for l in label if l != -100] for label in labels]
    true_predictions = [
        [label_names[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    all_metrics = metric.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": all_metrics["overall_precision"],
        "recall": all_metrics["overall_recall"],
        "f1": all_metrics["overall_f1"],
        "accuracy": all_metrics["overall_accuracy"],
    }

# Define the model
id2label = {str(i): label for i, label in enumerate(label_names)}
label2id = {v: k for k, v in id2label.items()}
model = AutoModelForTokenClassification.from_pretrained(model_checkpoint, id2label=id2label, label2id=label2id)

def objective(trial: optuna.Trial):
    model = AutoModelForTokenClassification.from_pretrained(model_checkpoint, id2label=id2label, label2id=label2id)
    
    wandb_config = dict(trial.params)
    wandb_config['trial_number'] = trial.number
    wandb.init(project=wandb_args['project'], reinit=True, group=wandb_args['group'], config=wandb_args)

    # Fine-tuning the model
    args = TrainingArguments(
        report_to=training_args['report_to'],
        output_dir=training_args['output_dir'],
        overwrite_output_dir=training_args['overwrite_output_dir'],
        evaluation_strategy=training_args['evaluation_strategy'],
        eval_steps=training_args['eval_steps'],
        optim=trial.suggest_categorical("optimizer", ["adamw_hf", "sgd", "adagrad"]),
        learning_rate=trial.suggest_float('learning_rate', low=training_args['lr_min'], high=training_args['lr_max']),
        num_train_epochs=trial.suggest_int('num_train_epochs', low = training_args['min_epochs'],high = training_args['max_epochs']),
        weight_decay=trial.suggest_float('weight_decay', training_args['wd_min'], training_args['wd_max']),
        per_device_train_batch_size=trial.suggest_categorical("per_device_train_batch_size", [4, 8, 16]),         
        per_device_eval_batch_size=training_args['per_device_eval_batch_size'],
        load_best_model_at_end=True,
        save_total_limit=3,
        disable_tqdm=True,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        tokenizer=tokenizer,
    )
    result = trainer.train()
    return result.training_loss

# Create Optuna Study
study = optuna.create_study(study_name=model_args['name_of_model'], direction='minimize') 
study.optimize(func=objective, n_trials=training_args['NUM_TRIALS'])  

# This can be used to train the final model. Passed through using kwargs into the model
print('Finding study best parameters')
best_lr = float(study.best_params['learning_rate'])
best_weight_decay = float(study.best_params['weight_decay'])
best_epoch = int(study.best_params['num_train_epochs'])
best_optimizer = str(study.best_params['optimizer'])
best_batch_size = int(study.best_params['per_device_train_batch_size'])

print('Extract best study params')
print(f'The best learning rate is: {best_lr}')
print(f'The best weight decay is: {best_weight_decay}')
print(f'The best epoch is : {best_epoch}')
print(f'The best optimizer is : {best_optimizer}')
print(f'The best batch size is : {best_batch_size}')

print('Create dictionary of the best hyperparameters')
best_hp_dict = {
    'best_learning_rate' : best_lr,
    'best_weight_decay': best_weight_decay,
    'best_epoch': best_epoch,
    'best_optimizer': best_optimizer,
    'best_batch_size': best_batch_size
}

wandb.init(project=wandb_args['project'], reinit=True, group=wandb_args['group'], config=wandb_args)

# Train Based on Optuna's Selected Hyperparams
print('Training the model on the custom parameters')
training_args = TrainingArguments(    
    report_to=training_args['report_to'],     
    output_dir=training_args['output_dir'], 
    optim=best_optimizer,
    learning_rate=best_lr,         
    weight_decay=best_weight_decay,         
    num_train_epochs=best_epoch,         
    per_device_train_batch_size=best_batch_size,         
    per_device_eval_batch_size=8,
    save_total_limit=3,
    disable_tqdm=True,         
)     

trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets['train'],
        eval_dataset=tokenized_datasets['validation'],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        tokenizer=tokenizer,
    )      
    
result = trainer.train() 
trainer.evaluate()

print('Saving the best Optuna tuned model')
if not os.path.exists('model'):
    os.mkdir('model')

model_path = "model/{}".format(model_args['name_of_model'])
model.save_pretrained(model_path)
tokenizer.save_pretrained(model_path)