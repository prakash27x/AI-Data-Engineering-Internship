# Task 02  · API → MySQL Pipeline
# Build the full data collection pipeline — fetch from internet, store in database
# Fetch user data from an API, store it in MySQL, and query it — complete automated pipeline.

import requests
import mysql.connector
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_url = os.getenv("API_URL")

try:
    # Fetching user data from the API
    response = requests.get(api_url)
    users_data = response.json()
    # print(json.dumps(users_data[0:2], indent=6))

    
    #Create app.db with a users table: id, name, email, phone, city, company_name
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
    )
    if conn.is_connected():
        print("Connected to MySQL server")
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS app")
    cursor.execute("USE app")
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY UNIQUE,
                name VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(255),
                city VARCHAR(255),
                company_name VARCHAR(255)
            )
    """)
    
    # Insert all users into the database with proper error handling
    for user in users_data:
        try:
            sql = """
                INSERT IGNORE INTO users (id, name, email, phone, city, company_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            values = (
                user.get("id"),
                user.get("name", "N/A"),
                user.get("email", "N/A"),
                user.get("phone", "N/A"),
                (user.get("address") or {}).get("city", "N/A"),
                (user.get("company") or {}).get("name", "N/A")
            )

            cursor.execute(sql, values)

        except mysql.connector.Error as err:
            print(f"Error inserting user {user.get('id')}: {err}")

    conn.commit()
    print("user Data inserted successfully!")

    print("\nQuery 1: Print all users sorted alphabetically by name")
    cursor.execute("SELECT name FROM users ORDER BY name ASC")
    result = cursor.fetchall()
    print(f"{'Name':45}")
    for (name,) in result:
        print(f"{name:45}")

    print("\nQuery 2: Find users from the same city (GROUP BY city, HAVING COUNT > 1)")
    cursor.execute("""
        SELECT city, COUNT(*) as user_count 
        FROM users      
        GROUP BY city
        HAVING user_count > 1
    """)
    result = cursor.fetchall()
    if not result:
        print("No cities with more than 1 user found.")
    else:
        print(f"{'City':45} {'User Count':>10}")
        for city, user_count in result:
            print(f"{city:45} {user_count:>10}")


    # -------------------------------------------------------------------------------------------
    # Add a second table posts — fetch from /posts and insert only posts by user_id 1, 2, and 3

    posts_response = requests.get(f"https://jsonplaceholder.typicode.com/posts")
    posts_data = posts_response.json()
    # print(json.dumps(posts_data[0:2], indent=6))
    cursor.execute("CREATE TABLE IF NOT EXISTS posts (id INT PRIMARY KEY UNIQUE, user_id INT, title VARCHAR(255), body TEXT)")
    inserted_count = 0
    for post in posts_data:
        if post.get("userId") in [1, 2, 3]:
            try:
                sql = """
                    INSERT IGNORE INTO posts (id, user_id, title, body)
                    VALUES (%s, %s, %s, %s)
                """

                values = (
                    post.get("id"),
                    post.get("userId"),
                    post.get("title", "N/A"),
                    post.get("body", "N/A")
                )
                cursor.execute(sql, values)
                inserted_count += 1

            except mysql.connector.Error as err:
                print(f"Error inserting post {post.get('id')}: {err}")
                
    conn.commit() # save changes to the database
    print(f"\n{inserted_count} posts inserted successfully.")

except Exception as e:
    print("Error while fetching data from API", e)
finally:
    if 'cursor' in locals():
        cursor.close()

    if 'conn' in locals() and conn.is_connected():
        conn.close()