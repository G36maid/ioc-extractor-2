import spacy

from spacy.symbols import ORTH

from entity import (
    attack_technique,
    bitcoin_address,
    cve,
    defender_threat,
    domain,
    email,
    filehash_md5,
    filehash_sha1,
    filehash_sha256,
    filepath,
    hostname,
    ipv4,
    ipv6,
    keyword,
    sslcert_fingerprint,
    uri,
    url,
)

parser = (
    defender_threat.parser
    | uri.parser
    | url.parser
    | email.parser
    | hostname.parser
    | domain.parser
    | sslcert_fingerprint.parser
    | ipv6.parser
    | ipv4.parser
    | cve.parser
    | attack_technique.parser
    | filepath.parser
    | filehash_sha256.parser  # len = 64
    | filehash_sha1.parser  # len = 40
    | bitcoin_address.parser  # len = 34
    | filehash_md5.parser  # len = 32
    # | keyword.make_parser(self.extracted_keywords)  # generate keywords parser
)

convert_cat_name = {
    'AttackTechnique': 'attackID', 'BitcoinAddress': 'bitcoinAddr', 'CVE': 'cve', 'MicrosoftDefenderThreat': 'defenderThreat',
    'domain': 'domain', 'email': 'email', 'FileHash-MD5': 'md5', 'FileHash-SHA1': 'sha1', 'FileHash-SHA256': 'sha256',
    'FilePath': 'filepath', 'hostname': 'hostname', 'IPv4': 'ipv4', 'IPv6': 'ipv6', 'SSLCertFingerprint': 'fingerprint',
    'URI': 'uri', 'URL': 'url', 'YARA': 'yara'
}

nlp = spacy.load("en_core_web_sm")
final_dataset = {"data": []}
  
def map_bio_tags(tags):
    next_element = 0
    bio_tags= []
    for x in range(len(tags)):
        element = tags[x]
        if element != 'O':
            if next_element == element:
                bio_tags.append(f'I-{element}')
            else:
                bio_tags.append(f'B-{element}')
        else:
            bio_tags.append(element)
        next_element = element
    return bio_tags
        
def add_entities(entity):
    entity_list = []
    if entity:
        for ents in entity:            
            if ents[0].getName() != 'URL' and ents[0].getName() != 'URI':
                special_case = [{ORTH: ents[0][0]}]
                nlp.tokenizer.add_special_case(ents[0][0], special_case)
                entity_list.append((ents[0][0], ents[0].getName()))
            else:
                if ents[0][0][-1] == '.':
                    special_case = [{ORTH: ents[0][0][:-1]}, {ORTH: "."}]
                    nlp.tokenizer.add_special_case(ents[0][0], special_case)
                    entity_list.append((ents[0][0][:-1], ents[0].getName()))
    return entity_list
        
def builder(line):
    # for idx, line in enumerate(article_list): # each sentence
    entities = list(parser.scanString(line))
    entity_list = add_entities(entities)
    doc = nlp(line)
    tokens = [w.text for w in doc]
    ner_tags = ["O" for w in doc]
    for idx, ele in enumerate(entity_list):
        try:
            ner_tags[tokens.index(ele[0])] = convert_cat_name[ele[1]]
        except:
            break
    bio_tags = map_bio_tags(ner_tags)
    final_dataset["data"].append({"tokens": tokens, "ner_tags": bio_tags})
    return final_dataset




