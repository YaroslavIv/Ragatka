
from flask import Flask
from typing import Any, Dict, List
from flask_socketio import SocketIO
from flask_cors import CORS
import threading

from authorization import Authorization
from registry import AUTH_DB_REGISTRY, EMBEDDING_REGISTRY, GENERATIVE_MODEL_REGISTRY
from client_db import ClientDB
from embedder import Embedder
from generative import Generative

class RagPipeline:
    def __init__(self) -> None:
        pass

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

            print(f'user_id: {user_id}')
            uuids = AUTH_DB_REGISTRY.build().get_docs(user_id)
            print(f'uuids: {uuids}')
            result = self.query(msg['text'], uuids)
            print(f'result: {result}')
            self.socketio.emit('message', result)

        except Exception as e:
            self.socketio.emit('error', {'error': str(e)})

    def query(self, query: str, uuids: List[str]) -> str:
        retrieved_doc = self.client_db.retrieve_document(query, uuids)
        print(f'retrieved_doc: {retrieved_doc}')
        print(f'query: {query}')
        generatived_text = self.generative.generative_text(retrieved_doc, query)

        print(f'generatived_text: {generatived_text}')

        return generatived_text

    def add_docs(self, docs: List[str]) -> None:
        self.client_db.add_documents(docs)
    
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
