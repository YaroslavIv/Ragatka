from typing import List, Dict, Any
from flask import Flask, request, jsonify
import threading
import os

from registry import DB_REGISTRY
from utils import read_file
from db import DB

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

        self.ALLOWED_EXTENSIONS = set(self.front_config.get('ALLOWED_EXTENSIONS', ['txt']))

        self.app = Flask(__name__)
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER

        self.add_routes()
    
    def allowed_file(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def add_routes(self) -> None:
        @self.app.route('/api/upload', methods=['POST'])
        def upload_files():
            if 'files' not in request.files:
                return jsonify({'error': 'No file part in the request'}), 400

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

                    docs.append(read_file(os.path.join(self.app.config['UPLOAD_FOLDER'], filename)))
            
            self.add_documents(docs)

            return jsonify({'message': 'Files uploaded successfully', 'files': saved_files}), 200

    def run_flask(self) -> None:
        if self.front_config:
            host = self.front_config.get('HOST', '0.0.0.0')
            port = self.front_config.get('PORT', 5000)
            self.app.run(host=host, port=port)
        else:
            print("Flask сервер не запущен, так как секция 'front' отсутствует в конфигурации")

    def run(self) -> None:
        if self.front_config:
            flask_thread = threading.Thread(target=self.run_flask)
            flask_thread.start()
        else:
            print("Flask сервер не запущен, так как секция 'front' отсутствует в конфигурации")

    def add_documents(self, docs: List[str]) -> None:
        self.db.add_documents(docs)
    
    def delete_file(self, doc: str) -> None:
        self.db.delete_file(doc)
    
    def retrieve_document(self, query: str) -> str:
        return self.db.retrieve_document(query)
    
    def search(self, doc: str) -> str:
        return self.db.search_file(doc)
