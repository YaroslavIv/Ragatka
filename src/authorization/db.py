import psycopg2
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from registry import AUTH_DB_REGISTRY

@dataclass(frozen=True)
class User:
    id: int
    email: str = field(default='')
    password_hash: str = field(default='')
    username: str = field(default='')

class AuthDB(ABC):

    @abstractmethod
    def search_by_name(self, email: str) -> User:
        pass

    @abstractmethod
    def search_by_id(self, user_id: str) -> User:
        pass

    @abstractmethod
    def add_docs(self, user_id: str, uuids: List[str]) -> None:
        pass

    @abstractmethod
    def get_docs(self, user_id: int) -> List[str]:
        pass

    @abstractmethod
    def delete_docs(self) -> None:
        pass

@AUTH_DB_REGISTRY.register_module
class PostgreSQL(AuthDB):
    def __init__(self, **cfg_db: Dict[str, Any]) -> None:
        """
        Инициализация класса с конфигурацией подключения к PostgreSQL.
        :param cfg_db: словарь с параметрами подключения к базе данных
        """
        self.cfg_db = cfg_db
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None

    def connect(self) -> None:
        """
        Подключается к базе данных PostgreSQL с использованием предоставленной конфигурации.
        """
        try:
            # Создаем подключение к базе данных
            self.connection = psycopg2.connect(**self.cfg_db)
            self.cursor = self.connection.cursor()
            print("Connected to the PostgreSQL database.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error while connecting to PostgreSQL: {error}")
            self.connection = None

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[list]:
        """
        Выполняет SQL-запрос.
        :param query: SQL-запрос в виде строки
        :param params: Параметры для SQL-запроса (если есть)
        :return: Результат выполнения запроса в виде списка строк (если запрос был SELECT)
        """
        if self.connection and self.cursor:
            try:
                self.cursor.execute(query, params)
                if query.strip().lower().startswith("select"):
                    result = self.cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(f"Error while executing query: {error}")
                return None
        else:
            print("No connection to PostgreSQL.")
            return None

    def close(self) -> None:
        """
        Закрывает курсор и соединение с базой данных.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("PostgreSQL connection is closed.")

    def search_by_name(self, email: str) -> Optional[User]:
        self.connect()
        result = self.execute_query("SELECT id, email, password_hash FROM users WHERE email=%s", email)
        self.close()

        if result:
            result = result[0]
            return User(
                id=result[0],
                email=result[1],
                password_hash=result[2]
            )
        
        return None
    
    def search_by_id(self, user_id: int) -> User:
        self.connect()
        result = self.execute_query("SELECT id, email, username FROM users WHERE id=%s", f"{user_id}")
        self.close()

        if result:
            result = result[0]
            return User(
                id=result[0],
                email=result[1],
                username=result[2]
            )
        
        return None
    
    def add_docs(self, user_id: int, uuids: List[str]) -> None:
        """
        Добавляет несколько документов для пользователя с указанным user_id.
        :param user_id: Идентификатор пользователя
        :param uuids: Список UUID документов
        """
        query = """
            INSERT INTO docs (user_id, uuid) 
            VALUES (%s, %s)
            ON CONFLICT (user_id, uuid) DO NOTHING;
        """
        
        params = [(user_id, uuid) for uuid in uuids]
        
        self.connect()
        for param in params:
            self.execute_query(query, param)
        self.close()


    def get_docs(self, user_id: int) -> List[str]:
        """
        Получает список UUID документов для пользователя с указанным user_id.
        :param user_id: Идентификатор пользователя
        :return: Список UUID документов
        """
        query = """
            SELECT uuid 
            FROM docs 
            WHERE user_id = %s;
        """
        
        self.connect()
        result = self.execute_query(query, (user_id,))
        self.close()
        
        return [row[0] for row in result] if result else []

    def delete_docs(self) -> None:
        self.connect()
        self.execute_query("DELETE FROM docs;")
        self.close()
