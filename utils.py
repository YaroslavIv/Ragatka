import os
import json
from typing import Any, Dict, List

def read_files(path_folder: str) -> List[str]:
    docs = []
    for file_name in os.listdir(path_folder):
        file = f'{path_folder}/{file_name}'
        if os.path.isfile(file) and len(file_name) > 4 and file_name[-3:] == 'txt':
            with open(file, 'r') as f:
                docs.append(' '.join(f.readlines()))
    
    return docs

def read_json(path_file: str) -> Dict[str, Any]:
    with open(path_file, 'r') as f:
        return json.load(f)
