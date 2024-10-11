from abc import ABC, abstractmethod

from registry import GENERATIVE_MODEL_REGISTRY
from openai import OpenAI

class Generative(ABC):

    @abstractmethod
    def generative_text(self, doc: str, quastion: str, max_length_doc: int = 1024) -> str:
        pass


@GENERATIVE_MODEL_REGISTRY.register_module
class APIOpenAI(Generative):
    def __init__(self, model: str) -> None:
        self.client = OpenAI()
        self.model = model
    
    def generative_text(self, doc: str, quastion: str, max_length_doc: int = 1024) -> str:
        content = f'quastion: {quastion}'
        if len(doc) > 0:
            content = f"rag information: {doc[:max_length_doc]}\n {content}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user", 
                    "content": content
                }
            ]
        )

        return response.choices[0].message.content
