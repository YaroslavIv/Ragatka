from typing import Any, Dict
import torch
from numpy import ndarray
from abc import ABC, abstractmethod
from transformers import AutoTokenizer, AutoModel
import sentence_transformers

from registry import EMBEDDING_REGISTRY

class Embedder(ABC):

    @abstractmethod
    def get_embedding(self, doc: str) -> ndarray:
        pass

@EMBEDDING_REGISTRY.register_module
class Auto(Embedder):
    def __init__(self, tokenizer: str, model: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self.model = AutoModel.from_pretrained(model)
    
    def get_embedding(self, doc: str) -> ndarray:
        inputs = self.tokenizer(doc, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding.squeeze().numpy()

@EMBEDDING_REGISTRY.register_module
class SentenceTransformer(Embedder):
    def __init__(self, model: str, **args: Dict[str, Any]) -> None:
        self.model = sentence_transformers.SentenceTransformer(model, **args)
    
    def get_embedding(self, doc: str) -> ndarray:
        return self.model.encode(doc)