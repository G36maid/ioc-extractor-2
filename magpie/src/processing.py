# import build_dataset
# import json
# import sys

# from read_reports import preprocess_article
# from os import listdir
# from os.path import join, exists

# my_path = "/Users/cyhsueh/Downloads/67741.html"
# id = sys.argv[1]
# print(f'Reading Folder {id}....')

# DIRPATH = join(my_path, id)
# invalid = ['PDF', 'pdf', '.DS_Store']
# try:
#     if exists(DIRPATH) == True: 
#         for f in listdir(DIRPATH):
#             if all(ele not in f for ele in invalid):
#                 file_name = join(DIRPATH, f)
#                 article_list = preprocess_article(file_name)
#                 if len(article_list) > 0:
#                     print(f'Start tokenizing File {f}....')
#                     for idx, line in enumerate(article_list):
#                         final_dataset = build_dataset.builder(line)
#                     with open(my_path + f'/annotated_data/{id}_{f}.json', "w") as output:
#                         json.dump(final_dataset, output, ensure_ascii=False)            
# except:
#     print(f'{id} not exists.')


import json
import sys
from read_reports import preprocess_article
from minio import Minio
from minio.error import S3Error
import build_dataset
import os

# MinIO client initialization
minio_client = Minio(
    "192.168.70.202:9000",  # replace with your MinIO server address
    access_key="cynthiachan",  # replace with your access key
    secret_key="Mynameis375!",  # replace with your secret key
    secure=False  # set to False if not using HTTPS
)

# Parameters
bucket_name = "feed-references"  # 你的 bucket 名称

# 設定桌面資料夾路徑
output_folder = "/Users/cyhsueh/Desktop/mino_data/"
os.makedirs(output_folder, exist_ok=True)

print('Reading all files in Bucket....')

invalid = ['PDF', 'pdf', '.DS_Store']

try:
    # 列出 bucket 中的所有檔案
    objects = minio_client.list_objects(bucket_name, recursive=True)
    
    for obj in objects:
        file_name = obj.object_name
        if all(ele not in file_name for ele in invalid):
            try:
                # 下載檔案內容
                response = minio_client.get_object(bucket_name, file_name)
                file_content = response.read().decode('utf-8')  # 解碼為文字
                
                # 處理檔案內容
                article_list = preprocess_article(file_content)
                if len(article_list) > 0:
                    print(f'Start tokenizing File {file_name}....')
                    final_dataset = []
                    for idx, line in enumerate(article_list):
                        dataset = build_dataset.builder(line)
                        final_dataset.extend(dataset)  # 將每個建構的 dataset 加入到 final_dataset 中
                    
                    # 將結果寫入到桌面上的指定資料夾中
                    output_file_name = os.path.join(output_folder, f'{os.path.basename(file_name)}.json')
                    with open(output_file_name, "w", encoding="utf-8") as output:
                        json.dump(final_dataset, output, ensure_ascii=False)
            except Exception as e:
                print(f'Error processing file {file_name}: {e}')
except S3Error as e:
    print(f'S3 Error: {e}')
except Exception as e:
    print(f'An error occurred: {e}')
