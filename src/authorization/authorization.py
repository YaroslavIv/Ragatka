from registry import AUTH_DB_REGISTRY
from authorization.db import AuthDB

import os
import threading
import datetime
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import jwt
from passlib.hash import bcrypt


class Authorization:
    _instance = None

    def __new__(cls, cfg_auth: Dict[str, Any] = None):
        if cls._instance is None:
            cls._instance = super(Authorization, cls).__new__(cls)
            cls._instance._initialize(cfg_auth)
        return cls._instance

    def _initialize(self, cfg_auth: Dict[str, Any]) -> None:
        if not hasattr(self, 'initialized') and cfg_auth:
            self.host = cfg_auth['HOST']
            self.port = cfg_auth['PORT']
            self.time = cfg_auth['TIME']
            self.init_db(cfg_auth['DB'])

            load_dotenv()
            self.app = Flask(__name__)
            CORS(self.app)
            self.app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

            self.run()

            self.initialized = True  # Чтобы предотвратить повторную инициализацию

            # Роут для входа
            @self.app.route('/api/login', methods=['POST'])
            def login():
                auth_data = request.json
                email = auth_data.get('email')
                password = auth_data.get('password')

                if not email or not password:
                    return jsonify({"error": "email and password are required"}), 400

                user = self.db.search_by_name(email)
                if user is None:
                    return jsonify({"error": "User not found"}), 404

                if not bcrypt.verify(password, user.password_hash):
                    return jsonify({"error": "Invalid password"}), 401

                token = self.create_jwt_token(user.id)
                return jsonify({"token": token})

            # Роут для получения данных пользователя
            @self.app.route('/api/user', methods=['GET'])
            def get_user_data():
                token = request.headers.get('Authorization')

                if not token:
                    return jsonify({'message': 'Token is missing'}), 403

                user_id = self.verify_jwt(token)
                if not user_id:
                    return jsonify({'message': 'Token is invalid'}), 403

                user = self.db.search_by_id(user_id)
                user_data = {
                    'userName': user.username,
                    'userEmail': user.email
                }
                return jsonify(user_data)

    @staticmethod
    def get_instance():
        if Authorization._instance is None:
            raise Exception("Authorization class has not been initialized with a configuration.")
        return Authorization._instance

    def init_db(self, db: Dict[str, Any]) -> None:
        self.db: AuthDB = AUTH_DB_REGISTRY.build(db)

    def run_flask(self) -> None:
        self.app.run(host=self.host, port=self.port)

    def run(self) -> None:
        flask_thread = threading.Thread(target=self.run_flask)
        flask_thread.start()

    def verify_jwt(self, token) -> Optional[str]:
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=["HS256"])
            return data['user_id']
        except:
            return None

    def create_jwt_token(self, user_id: int) -> str:
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=self.time)
        }
        token = jwt.encode(payload, self.app.config['SECRET_KEY'], algorithm='HS256')
        return token

    def delete_docs(self) -> None:
        self.db.delete_docs()