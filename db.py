from typing import List
import weaviate
from abc import ABC, abstractmethod

from registry import DB_REGISTRY, EMBEDDING_REGISTRY
from embedder import Embedder

class DB(ABC):

    @abstractmethod
    def add_documents(self, docs: List[str]) -> None:
        pass

    @abstractmethod
    def retrieve_document(self, query: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, doc: str) -> None:
        pass
    
    @abstractmethod
    def search_file(self, doc: str, certainty: float) -> str:
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
        self.embedder: Embedder = EMBEDDING_REGISTRY.build()


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
    
    def add_documents(self, docs: List[str]) -> None:
        for doc in docs:
            if len(self.search_file(doc)) == 0:
                self.client.data_object.create(
                    class_name=self.class_name,
                    data_object={
                        "doc": doc
                    },
                    vector=self.embedder.get_embedding(doc)
                )
    
    def retrieve_document(self, query: str) -> str:
        query_embedding = self.embedder.get_embedding(query)

        response = self.client.query.get(self.class_name, ["doc"]).with_near_vector({
            "vector": query_embedding.tolist(),
        }).do()
        
        return response['data']['Get'][self.class_name][0]['doc'] if response['data']['Get'][self.class_name] else ''
    
    def delete_file(self, doc: str) -> None:
        uuid = self.search_file(doc, self.embedder.get_embedding)
        
        if len(uuid) > 0:
            self.client.data_object.delete(uuid)
    
    def search_file(self, doc: str, certainty: float = 0.999) -> str:

        response = self.client.query.get(self.class_name, ["_additional { id }"]) \
            .with_near_vector({"vector": self.embedder.get_embedding(doc).tolist(), "certainty": certainty}) \
            .do()

        uuid = ''
        if response and "data" in response and "Get" in response["data"] and response["data"]["Get"][self.class_name]:
            uuid = response["data"]["Get"][self.class_name][0]["_additional"]["id"]

        return uuid