# Task 01 · Create, Insert & Query
#  Building first MySQL database from scratch

import mysql.connector
from books_data import sample_books_list # importing sample books data from books_data.py

# connecting to MySQL server and creating a database named 'library'
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
    )
    if conn.is_connected():
        print("Connected to MySQL server")
    cursor = conn.cursor() # creating a cursor object to execute SQL queries
    cursor.execute("CREATE DATABASE IF NOT EXISTS library") 
    cursor.execute("USE library")
    cursor.execute("CREATE TABLE IF NOT EXISTS books (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), author VARCHAR(255), year INT, genre VARCHAR(255), rating REAL)")

    cursor.execute("ALTER TABLE books ADD UNIQUE (title)")

    # inserting sample books data into the 'books' table
    cursor.executemany("INSERT IGNORE INTO books (title, author, year, genre, rating) VALUES (%s, %s, %s, %s, %s)", sample_books_list)
    conn.commit() # commit is necessary to save the changes to the database
    print(f"{cursor.rowcount} records inserted into the 'books' table")
    
    data = cursor.fetchall() # fetching all the data from the 'books' table
    for row in data:
        print(row)
    
except Exception as e:
    print("Error while connecting to MySQL", e)
finally:
    if 'cursor' in locals():
        cursor.close()

    if 'conn' in locals() and conn.is_connected():
        conn.close()
