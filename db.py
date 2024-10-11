from typing import List, Callable
import weaviate
from numpy import ndarray
from abc import ABC, abstractmethod

from registry import DB_REGISTRY

class DB(ABC):

    @abstractmethod
    def add_documents(self, docs: List[str], get_embedding: Callable[[str], ndarray]) -> None:
        pass

    @abstractmethod
    def retrieve_document(self, query: str, get_embedding: Callable[[str], ndarray]) -> str:
        pass

@DB_REGISTRY.register_module
class WeaviateDB(DB):
    def __init__(
        self, 
        url: str,
        class_name: str
    ) -> None:
        super().__init__()

        self.client = weaviate.Client(url=url)
        self.create(class_name)
    
    def create(self, class_name: str) -> None:
        self.class_name = class_name
        self.client.schema.delete_class(class_name)
        self.client.schema.create_class({
            "class": class_name,
            "properties": [
                {
                    "name": "doc",
                    "dataType": ["text"]
                }
            ]
        })
    
    def add_documents(self, docs: List[str], get_embedding: Callable[[str], ndarray]) -> None:
        for doc in docs:
            self.client.data_object.create(
                class_name=self.class_name,
                data_object={
                    "doc": doc
                },
                vector=get_embedding(doc)
            )
    
    def retrieve_document(self, query: str, get_embedding: Callable[[str], ndarray]) -> str:
        query_embedding = get_embedding(query)

        response = self.client.query.get(self.class_name, ["doc"]).with_near_vector({
            "vector": query_embedding.tolist(),
        }).do()
        
        print(response)
        # Извлечение текста первого найденного документа
        return response['data']['Get'][self.class_name][0]['doc'] if response['data']['Get'][self.class_name] else ''