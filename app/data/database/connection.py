
import mysql.connector
from mysql.connector import Error

from app.core.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_CONNECT_TIMEOUT,
)


class DatabaseConnection:

    @staticmethod
    def connect():
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connection_timeout=DB_CONNECT_TIMEOUT,
        )

    @staticmethod
    def test_connection() -> bool:
        connection = None

        try:
            connection = DatabaseConnection.connect()
            return bool(connection.is_connected())

        except Error:
            return False

        finally:
            if connection is not None:
                connection.close()
