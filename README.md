# RAGATKA
<b>RAGATKA</b> - Retrieval-Augmented Generation And Task Knowledge Assistance

## Run

### weaviate
```bash
docker run -p 8080:8080 -p 50051:50051 --name weaviate cr.weaviate.io/semitechnologies/weaviate:1.26.6
```
### docs

#### Add files inside the folder.
```bash
python main.py add <cfg_db> <cfg_embeder> <path_folder>
```

#### Delete file
```bash
python main.py delete <cfg_db> <cfg_embeder> <path_file>
```

#### Search file
```bash
python main.py search <cfg_db> <cfg_embeder> <path_file>
```

### question

```bash
python main.py question <cfg_db> <cfg_embeder> <cfg_generative> <question>
```

## Install

### weaviate
```bash
docker pull cr.weaviate.io/semitechnologies/weaviate:1.26.6
```

### dependencies
```bash
pip install -r requirements.txt
```