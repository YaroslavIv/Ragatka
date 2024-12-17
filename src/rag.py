
from flask import Flask
from typing import Any, Dict, List, Optional
from flask_socketio import SocketIO
from flask_cors import CORS
import threading

from authorization import Authorization
from registry import AUTH_DB_REGISTRY, EMBEDDING_REGISTRY, GENERATIVE_MODEL_REGISTRY
from vector_db import ClientDB
from embedder import Embedder
from generative import Generative
import json

class RagPipeline:
    def __init__(self) -> None:
        self.name_json = 'output.json'
        with open(self.name_json, 'w') as f:
            json.dump({}, f)
        self.index = 1

    def init_db(self, cfg_db: Dict[str, str]) -> None:
        self.client_db = ClientDB(cfg_db)
    
    def init_embeder(self, cfg_embeder: Dict[str, str]) -> None:
        self.embeder : Embedder = EMBEDDING_REGISTRY.build(cfg_embeder)
    
    def init_generative(self, cfg_generative: Dict[str, str]) -> None:
        self.generative : Generative = GENERATIVE_MODEL_REGISTRY.build(cfg_generative)
    
    def init_auth(self, cfg_auth: Dict[str, Any]) -> None:
        self.auth = Authorization(cfg_auth)

    def init_chat(self, cfg_chat: Dict[str, str]) -> None:
        self.host = cfg_chat['HOST']
        self.port = cfg_chat['PORT']

        self.app = Flask(__name__)
        CORS(self.app)

        self.socketio = SocketIO(self.app, cors_allowed_origins="*", ping_timeout=120, ping_interval=25)

        @self.socketio.on('message')
        def handle_message(msg: str):
            self.socketio.start_background_task(self.process_heavy_task, msg)

    def process_heavy_task(self, msg):
        try:
            token = msg.get('token')
            user_id = self.auth.verify_jwt(" " + token) 
            if not user_id:
                self.socketio.emit('error', {'error': 'Invalid JWT token'})
                return

            uuids = AUTH_DB_REGISTRY.build().get_docs(user_id)
            result = self.query(msg['text'], msg['chat'], uuids, 5)
            self.socketio.emit('message', result)

        except Exception as e:
            self.socketio.emit('error', {'error': str(e)})

    def query(self, query: str, chat: str, uuids: List[str], max_retrieve_document: int = 1) -> str:
        retrieved_docs = self.client_db.retrieve_document(query, uuids, max_retrieve_document)
        print(f'retrieved_doc: {retrieved_docs}')
        print(f'query: {query}')
        print(f'chat: {chat}')

        generatived_text = self.generative.generative_text(chat, retrieved_docs, query)
        print(f'generatived_text: {generatived_text}')

        return generatived_text

    def add_docs(self, docs: List[str]) -> Optional[List[str]]:
        return self.client_db.add_documents(docs)
    
    def delete_file(self, doc: str) -> None:
        self.client_db.delete_file(doc)
    
    def search(self, doc: str) -> None:
        uuid = self.client_db.search(doc)
        if len(uuid) > 0:
            print(f"Found object with UUID: {uuid}")
        else:
            print("No object found.")
    
    def chat(self) -> None:
        """
        Запуск Flask-сервера с SocketIO.
        """
        if self.app is None or self.socketio is None:
            raise RuntimeError("Chat server is not initialized. Call init_chat() first.")

        def run_server():
            self.socketio.run(self.app, host=self.host, port=self.port)

        server_thread = threading.Thread(target=run_server)
        server_thread.start()
