from typing import List, Dict, Any, Optional
from flask import Flask, request, jsonify
import threading
import os

from flask_cors import CORS

from authorization import Authorization
from registry import DB_REGISTRY, AUTH_DB_REGISTRY
from utils import read_txt_file, read_pdf_file
from vector_db.db import DB

class ClientDB:
    def __init__(
        self, 
        cfg: Dict[str, Any]
    ) -> None:

        self.front_config : Dict[str, Any] = cfg.pop('front', None)
        
        if self.front_config:
            self.initialize_flask()

            if self.front_config.get('RUN', False):
                self.run()

        self.db : DB = DB_REGISTRY.build(cfg)

    def initialize_flask(self) -> None:
        self.UPLOAD_FOLDER = self.front_config.get('UPLOAD_FOLDER', './uploads')
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)

        self.ALLOWED_EXTENSIONS = set(self.front_config.get('ALLOWED_EXTENSIONS', ['txt', 'pdf']))

        self.app = Flask(__name__)
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER

        CORS(self.app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True, expose_headers='Authorization')
        
        @self.app.route('/api/upload', methods=['POST'])
        def upload_files():
            if 'files' not in request.files:
                return jsonify({'error': 'No file part in the request'}), 400

            token = request.headers.get('Authorization')
            user_id = Authorization().get_instance().verify_jwt(token)
            if not user_id:
                return jsonify({'error': 'Invalid JWT token'}), 400
                
            
            files = request.files.getlist('files')

            if not files or len(files) == 0:
                return jsonify({'error': 'No files uploaded'}), 400

            saved_files = []
            docs = []
            for file in files:
                if file and self.allowed_file(file.filename):
                    filename = file.filename
                    file.save(os.path.join(self.app.config['UPLOAD_FOLDER'], filename))
                    saved_files.append(filename)
                    
                    if file.filename[-3:] == 'txt':
                        docs.append(read_txt_file(os.path.join(self.app.config['UPLOAD_FOLDER'], filename)))
                    elif file.filename[-3:] == 'pdf':
                        docs += read_pdf_file(os.path.join(self.app.config['UPLOAD_FOLDER'], filename))

            uuids = self.add_documents(docs)
            AUTH_DB_REGISTRY.build().add_docs(user_id, uuids)

            return jsonify({'message': 'Files uploaded successfully', 'files': saved_files}), 200
    
    def allowed_file(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def run_flask(self) -> None:
        if self.front_config:
            host = self.front_config.get('HOST', '0.0.0.0')
            port = self.front_config.get('PORT', 5001)
            self.app.run(host=host, port=port)
        else:
            print("Flask сервер не запущен, так как секция 'front' отсутствует в конфигурации")

    def run(self) -> None:
        if self.front_config:
            flask_thread = threading.Thread(target=self.run_flask)
            flask_thread.start()
        else:
            print("Flask сервер не запущен, так как секция 'front' отсутствует в конфигурации")

    def add_documents(self, docs: List[str]) -> Optional[List[str]]:
        return self.db.add_documents(docs)
    
    def delete_file(self, doc: str) -> None:
        self.db.delete_file(doc)
    
    def delete(self) -> None:
        self.db.delete()
    
    def retrieve_document(self, query: str, uuids: List[str], max_retrieve_document: int) -> List[str]:
        return self.db.retrieve_document(query, uuids, max_retrieve_document)
    
    def search(self, doc: str) -> str:
        return self.db.search_file(doc)
