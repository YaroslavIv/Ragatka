import torch
import transformers
from openai import OpenAI
from abc import ABC, abstractmethod

from registry import GENERATIVE_MODEL_REGISTRY

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

@GENERATIVE_MODEL_REGISTRY.register_module
class Transformers(Generative):
    def __init__(self, model: str, torch_dtype: str, device_map: str) -> None:
        self.model = model
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.model,
            torch_dtype=eval(torch_dtype), 
            device_map=device_map
        )
        self.terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("") or self.pipeline.tokenizer.eos_token_id
        ]
    
    def generative_text(self, doc: str, quastion: str, max_length_doc: int = 1024) -> str:
        content = [{"role": "user", "content": quastion}]
        if len(doc) > 0:
            content = [{"role": "system", "content": doc}] + content
        
        prompt = self.pipeline.tokenizer.apply_chat_template(
            content, tokenize=False, add_generation_prompt=True
        )
        
        outputs = self.pipeline(
            prompt,
            max_new_tokens=max_length_doc,
            eos_token_id=self.terminators[0],  # Используем первый элемент, если он валиден
            do_sample=True,
        )

        return outputs[0]["generated_text"][len(prompt):]
