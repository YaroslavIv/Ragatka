from typing import Any, List, Callable
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

    @abstractmethod
    def delete_file(self, doc: str, get_embedding: Callable[[str], ndarray]) -> None:
        pass
    
    @abstractmethod
    def search_file(self, doc_embedding: List[Any], certainty: float) -> str:
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
        schema = self.client.schema.get()['classes']

        if not any(cls['class'] == class_name for cls in schema):
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
            doc_embedding = get_embedding(doc)

            if len(self.search_file(doc_embedding)) == 0:
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
        
        return response['data']['Get'][self.class_name][0]['doc'] if response['data']['Get'][self.class_name] else ''
    
    def delete_file(self, doc: str, get_embedding: Callable[[str], ndarray]) -> None:
        uuid = self.search_file(doc, get_embedding)
        
        if len(uuid) > 0:
            self.client.data_object.delete(uuid)
    
    def search_file(self, doc_embedding: List[Any], certainty: float = 0.999) -> str:

        response = self.client.query.get(self.class_name, ["_additional { id }"]) \
            .with_near_vector({"vector": doc_embedding, "certainty": certainty}) \
            .do()

        uuid = ''
        if response and "data" in response and "Get" in response["data"] and response["data"]["Get"][self.class_name]:
            uuid = response["data"]["Get"][self.class_name][0]["_additional"]["id"]

        return uuid