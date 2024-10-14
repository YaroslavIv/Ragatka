import os
import json
from typing import Any, Dict, List

def read_file(path_file: str) -> str:
    doc = ''
    file_name = path_file.split(os.path.sep)[-1]
    if os.path.isfile(path_file) and len(file_name) > 4 and file_name[-3:] == 'txt':
        with open(path_file, 'r') as f:
            doc = ' '.join(f.readlines())
    
    return doc

def read_files(path_folder: str) -> List[str]:
    docs = []
    for file_name in os.listdir(path_folder):
        doc =read_file(f'{path_folder}/{file_name}')
        if len(doc) > 0:
            docs.append(doc)
    
    return docs

def read_json(path_file: str) -> Dict[str, Any]:
    with open(path_file, 'r') as f:
        return json.load(f)
