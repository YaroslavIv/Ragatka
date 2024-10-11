
from typing import Dict, List

from registry import EMBEDDING_REGISTRY, GENERATIVE_MODEL_REGISTRY
from client_db import ClientDB
from embedder import Embedder
from generative import Generative

class RagPipeline:
    def __init__(
        self, 
        cfg_db: Dict[str, str], 
        cfg_embeder: Dict[str, str],
        cfg_generative: Dict[str, str],

    ) -> None:
        
        self.client_db = ClientDB(cfg_db)
        self.embeder : Embedder = EMBEDDING_REGISTRY.build(cfg_embeder)
        self.generative : Generative = GENERATIVE_MODEL_REGISTRY.build(cfg_generative)

    def run(
        self,
        docs: List[str],
        query: str
    ) -> None:
        self.client_db.add_documents(docs, self.embeder.get_embedding)

        retrieved_doc = self.client_db.retrieve_document(query, self.embeder.get_embedding)

        print(f'retrieved_doc: {retrieved_doc}')
        print(f'query: {query}')
        generatived_text = self.generative.generative_text(retrieved_doc, query)

        print(f'generatived_text: {generatived_text}')
