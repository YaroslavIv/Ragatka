
from typing import Dict, List

from registry import EMBEDDING_REGISTRY, GENERATIVE_MODEL_REGISTRY
from client_db import ClientDB
from embedder import Embedder
from generative import Generative

class RagPipeline:
    def __init__(self) -> None:
        pass

    def init_db(self, cfg_db: Dict[str, str]) -> None:
        self.client_db = ClientDB(cfg_db)
    
    def init_embeder(self, cfg_embeder: Dict[str, str]) -> None:
        self.embeder : Embedder = EMBEDDING_REGISTRY.build(cfg_embeder)
    
    def init_generative(self, cfg_generative: Dict[str, str]) -> None:
        self.generative : Generative = GENERATIVE_MODEL_REGISTRY.build(cfg_generative)
        

    def query(self, query: str) -> None:
        retrieved_doc = self.client_db.retrieve_document(query, self.embeder.get_embedding)

        print(f'retrieved_doc: {retrieved_doc}')
        print(f'query: {query}')
        generatived_text = self.generative.generative_text(retrieved_doc, query)

        print(f'generatived_text: {generatived_text}')

    def add_docs(self, docs: List[str]) -> None:
        self.client_db.add_documents(docs, self.embeder.get_embedding)
    
    def delete_file(self, doc: str) -> None:
        self.client_db.delete_file(doc, self.embeder.get_embedding)
    
    def search(self, doc: str) -> None:
        uuid = self.client_db.search(self.embeder.get_embedding(doc).tolist())
        if len(uuid) > 0:
            print(f"Found object with UUID: {uuid}")
        else:
            print("No object found.")
    