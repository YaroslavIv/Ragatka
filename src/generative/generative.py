from typing import List
import transformers
from openai import OpenAI
from abc import ABC, abstractmethod

from registry import GENERATIVE_MODEL_REGISTRY

class Generative(ABC):

    @abstractmethod
    def generative_text(self, chat: str, docs: List[str], question: str, max_length_doc: int = 1024) -> str:
        pass


@GENERATIVE_MODEL_REGISTRY.register_module
class APIOpenAI(Generative):
    def __init__(self, model: str, max_history_length: int) -> None:
        self.client = OpenAI()
        self.model = model
        self.history = {}
        self.max_history_length = max_history_length
    
    def add_to_history(self, chat: str,  role: str, message: str):
        """
        Добавляет новое сообщение в историю.
        :param role: Роль отправителя сообщения (user или system)
        :param message: Текст сообщения
        """

        if chat in self.history:
            self.history[chat].append({"role": role, "content": message})
        else:
            self.history[chat] = [{"role": role, "content": message}]

        if len(self.history) > self.max_history_length:
            self.history.pop(0)

    def generative_text(self, chat: str, docs: List[str], question: str, max_length_doc: int = 1024) -> str:
        self.add_to_history(chat, "user", question)

        for doc in docs: 
            if len(doc) > 0:
                self.add_to_history(chat, "user", doc)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history[chat]
        )

        generated_text = response.choices[0].message.content
        self.add_to_history(chat, "system", generated_text)

        return generated_text

@GENERATIVE_MODEL_REGISTRY.register_module
class Transformers(Generative):
    def __init__(self, model: str, torch_dtype: str, device_map: str, max_history_length: int) -> None:
        self.model = model
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.model,
            torch_dtype=eval(torch_dtype), 
            device_map=device_map
        )

        self.history = {}
        self.max_history_length = max_history_length

        self.terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("") or self.pipeline.tokenizer.eos_token_id
        ]
    
    def add_to_history(self, chat: str,  role: str, message: str):
        """
        Добавляет новое сообщение в историю.
        :param role: Роль отправителя сообщения (user или system)
        :param message: Текст сообщения
        """

        if chat in self.history:
            self.history[chat].append({"role": role, "content": message})
        else:
            self.history[chat] = [{"role": role, "content": message}]

        if len(self.history) > self.max_history_length:
            self.history.pop(0)

    def generative_text(self, chat: str, docs: List[str], question: str, max_length_doc: int = 1024) -> str:
        """
        Генерирует ответ с учётом истории диалога.
        :param question: Вопрос пользователя
        :param max_length_doc: Максимальная длина генерируемого текста
        :return: Сгенерированный текст
        """

        self.add_to_history(chat, "user", question)

        for doc in docs: 
            if len(doc) > 0:
                self.add_to_history(chat, "user", doc)
        
        prompt = self.pipeline.tokenizer.apply_chat_template(
            self.history[chat], tokenize=False, add_generation_prompt=True
        )
        
        outputs = self.pipeline(
            prompt,
            max_new_tokens=max_length_doc,
            eos_token_id=self.terminators[0],  # Используем первый элемент, если он валиден
            do_sample=True,
        )

        generated_text = outputs[0]["generated_text"][len(prompt):]
        self.add_to_history(chat, "system", generated_text)

        return generated_text
