"""
MySQL Database Connection
"""

import mysql.connector
from mysql.connector import Error

# ==========================================
# Database Configuration
# ==========================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "nepse_analyzer",
    "charset": "utf8mb4"
}


def get_db_connection():
    """
    Create and return a MySQL database connection.
    """

    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            return connection

    except Error as e:
        print(f"MySQL Connection Error: {e}")

    return None


def close_connection(connection):
    """
    Close database connection safely.
    """

    if connection and connection.is_connected():
        connection.close()