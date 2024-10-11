from typing import Callable, List, Dict, Any
from numpy import ndarray


from registry import DB_REGISTRY
from db import DB

class ClientDB:
    def __init__(
        self, 
        cfg: Dict[str, Any]
    ) -> None:
        self.db : DB = DB_REGISTRY.build(cfg)
    
    def add_documents(self, docs: List[str], get_embedding: Callable[[str], ndarray]) -> None:
        self.db.add_documents(docs, get_embedding)
    
    def retrieve_document(self, query: str, get_embedding: Callable[[str], ndarray]) -> str:
        return self.db.retrieve_document(query, get_embedding)
