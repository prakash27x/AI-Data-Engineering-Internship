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
    cursor.execute("CREATE TABLE IF NOT EXISTS books (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) UNIQUE, author VARCHAR(255), year INT, genre VARCHAR(255), rating REAL)")

    # inserting sample books data into the 'books' table
    cursor.executemany("INSERT IGNORE INTO books (title, author, year, genre, rating) VALUES (%s, %s, %s, %s, %s)", sample_books_list)
    conn.commit() # commit is necessary to save the changes to the database
    print(f"{cursor.rowcount} records inserted into the 'books' table")
    
    print("--------------------------------")
    print("Answering the following queries: \n")
    print("Query 1: SELECT all books published after 2000, ordered by rating (highest first)")
    print(f"{'Title':45} {'Year':>6} {'Rating':>6}")
    cursor.execute("SELECT title,year,rating FROM books WHERE year > %s ORDER BY rating DESC", (2000,))
    result = cursor.fetchall()
    for title, year, rating in result:
        print(f"{title:45} {year:>6} {rating:>6.1f}")

    print("\nQuery 2: SELECT all books in the 'Fiction' genre with rating above 4.0")
    print(f"{'Title':45} {'Rating':>6}")
    cursor.execute("SELECT title,rating FROM books WHERE genre = %s AND rating > %s", ('Fiction', 4.0))
    result = cursor.fetchall()
    for title, rating in result:
        print(f"{title:45} {rating:>6.1f}")

    print("\nQuery 3: Find the average rating across all books")
    cursor.execute("SELECT AVG(rating) FROM books")
    result = cursor.fetchone()
    print(f"Average Rating: {result[0]:.2f}")

    print("\nQuery 4: Count how many books exist per genre")
    cursor.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre")
    result = cursor.fetchall()
    print(f"{'Genre':45} {'Count':>7}")
    for genre, count in result:
        print(f"{genre:45} {count:>6}")

except Exception as e:
    print("Error while connecting to MySQL", e)
finally:
    if 'cursor' in locals():
        cursor.close()

    if 'conn' in locals() and conn.is_connected():
        conn.close()
