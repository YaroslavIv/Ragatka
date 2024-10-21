import os
import json
import PyPDF2
from typing import Any, Dict, List

def read_txt_file(path_file: str) -> str:
    doc = ''
    file_name = path_file.split(os.path.sep)[-1]
    if os.path.isfile(path_file) and len(file_name) > 4 and file_name[-3:] == 'txt':
        with open(path_file, 'r') as f:
            doc = ' '.join(f.readlines())
    
    return doc

def read_pdf_file(path_file: str, max_length: int = 1_000) -> List[str]:
    """
    Читает PDF файл, извлекает текст и разбивает его на части длиной до max_length.
    :param path_file: Путь к PDF файлу
    :param max_length: Максимальная длина каждого блока текста (в символах)
    :return: Список частей текста
    """

    with open(path_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        for i, page in enumerate(reader.pages):
            print(f'{i}/{len(reader.pages)}')
            full_text += page.extract_text()

    chunks = [full_text[i:i+max_length] for i in range(0, len(full_text), max_length)]
    
    return chunks

def read_txt_files(path_folder: str) -> List[str]:
    docs = []
    for file_name in os.listdir(path_folder):
        doc = read_txt_file(f'{path_folder}/{file_name}')
        if len(doc) > 0:
            docs.append(doc)
    
    return docs

def read_json(path_file: str) -> Dict[str, Any]:
    with open(path_file, 'r') as f:
        return json.load(f)
