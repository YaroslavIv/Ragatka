import PyPDF2

def pdf_to_files(path_file: str, max_length: int = 1_000) -> None:
    with open(path_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        for i, page in enumerate(reader.pages):
            print(f'READ: {i}/{len(reader.pages)}')
            full_text += page.extract_text()

    chunks = [full_text[i:i+max_length] for i in range(0, len(full_text), max_length)]

    for i, text in enumerate(chunks):
        print(f'WRITE: {i}/{len(chunks)}')
        with open(f'{path_file.split(".")[0]}_{str(i).zfill(3)}.txt', 'w') as f:
            f.write(text)
