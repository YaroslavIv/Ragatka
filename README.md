# RAGATKA
<b>RAGATKA</b> - Retrieval-Augmented Generation And Task Knowledge Assistance

## Run

### weaviate and postgres
```bash
docker-compose up -d
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

### weaviate and postgres
```bash
docker pull cr.weaviate.io/semitechnologies/weaviate:1.26.6
docker pull postgres:latest
```

### dependencies
```bash
pip install -r requirements.txt
```