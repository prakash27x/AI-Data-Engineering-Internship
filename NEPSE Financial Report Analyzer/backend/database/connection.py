"""
MySQL Database Connection
"""

import mysql.connector
from mysql.connector import Error

from core.config import settings


def get_db_connection():
    """
    Create and return a MySQL database connection.
    """
    try:
        return mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset="utf8mb4",
        )

    except Error as e:
        print(f"MySQL Connection Error: {e}")
        return None


def close_connection(connection):
    """
    Close database connection safely.
    """
    if connection and connection.is_connected():
        connection.close()