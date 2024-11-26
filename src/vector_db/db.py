from typing import List, Optional
import weaviate
from abc import ABC, abstractmethod

from registry import DB_REGISTRY, EMBEDDING_REGISTRY
from embedder import Embedder

class DB(ABC):

    @abstractmethod
    def add_documents(self, docs: List[str]) -> Optional[List[str]]:
        pass

    @abstractmethod
    def retrieve_document(self, query: str, uuids: List[str], max_retrieve_document: int) -> List[str]:
        pass

    @abstractmethod
    def delete_file(self, doc: str) -> None:
        pass
    
    @abstractmethod
    def search_file(self, doc: str, certainty: float) -> str:
        pass

    @abstractmethod
    def delete(self) -> None:
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
    
    def delete(self) -> None:
        self.client.schema.delete_class(self.class_name)
    
    def add_documents(self, docs: List[str]) -> Optional[List[str]]:
        uuids = []
        for doc in docs:
            if len(self.search_file(doc)) == 0:
                uuid = self.client.data_object.create(
                    class_name=self.class_name,
                    data_object={
                        "doc": doc
                    },
                    vector=self.embedder.get_embedding(doc)
                )
                uuids.append(uuid)
        return uuids
    
    def retrieve_document(self, query: str, uuids: List[str], max_retrieve_document: int) -> List[str]:
        query_embedding = self.embedder.get_embedding(query)

        where_filter = {
            "operator": "Or",
            "operands": [
                {
                    "path": ["id"],
                    "operator": "Equal",
                    "valueString": uuid
                } for uuid in uuids
            ]
        }

        response = self.client.query.get(self.class_name, ["doc"]).with_near_vector({
            "vector": query_embedding.tolist(),
        }).with_where(where_filter).do()

        response = response['data']['Get'][self.class_name]
        
        return [data['doc'] for data in response[:max_retrieve_document] if 'doc' in data] if response else ['']
    
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