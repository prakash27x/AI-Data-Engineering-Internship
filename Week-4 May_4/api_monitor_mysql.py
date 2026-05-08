# Task B · API Monitor with Change Detection 

import json
import random
import mysql.connector
from urllib.request import urlopen
from datetime import datetime

# API endpoint for posts
BASE_URL = "https://jsonplaceholder.typicode.com/posts"

# Timestamp for this execution
RUN_TIME = datetime.now()

conn = None
cursor = None

# STEP 1: FETCH DATA FROM API
def fetch_data():
    try:
        response = urlopen(BASE_URL)
        return json.loads(response.read())
    except Exception as err:
        print(f"Error fetching API data: {err}")
        return None

# STEP 2: CREATE DATABASE + TABLES
def create_db():
    global conn, cursor
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
        )
        cursor = conn.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS monitor_db")
        cursor.execute("USE monitor_db")

        # Table to store latest state of posts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id INT PRIMARY KEY,
                userId INT,
                title VARCHAR(255),
                body TEXT
            )
        """)

        # Table to track all changes (NEW / MODIFIED)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS change_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                post_id INT,
                change_type VARCHAR(20),
                old_title VARCHAR(255),
                new_title VARCHAR(255),
                old_body TEXT,
                new_body TEXT,
                run_time DATETIME,
                FOREIGN KEY (post_id) REFERENCES posts(post_id)
            )
        """)

        # MIGRATION CHECK (important for future runs when we add new columns)
        cursor.execute("SHOW COLUMNS FROM change_log LIKE 'run_time'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE change_log ADD COLUMN run_time DATETIME NULL")

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Database setup error: {err}")


# STEP 3: COMPARE API VS DB
def monitor_posts(api_posts):
    global conn, cursor
    try:
        for post in api_posts:

            # Check if post already exists in DB
            cursor.execute(
                "SELECT userId, title, body FROM posts WHERE post_id = %s",
                (post["id"],),
            )
            existing = cursor.fetchone()

            # CASE 1: NEW POST → INSERT INTO DB + LOG
            if existing is None:
                cursor.execute(
                    """
                    INSERT INTO posts (post_id, userId, title, body)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (post["id"], post["userId"], post["title"], post["body"]),
                )

                cursor.execute(
                    """
                    INSERT INTO change_log 
                    (post_id, change_type, old_title, new_title, old_body, new_body, run_time)
                    VALUES (%s, 'NEW', NULL, %s, NULL, %s, %s)
                    """,
                    (post["id"], post["title"], post["body"], RUN_TIME),
                )

            # CASE 2: EXISTING POST → CHECK CHANGES
            else:
                old_user_id, old_title, old_body = existing

                # Detect modification
                if old_title != post["title"] or old_body != post["body"]:

                    # Log modification
                    cursor.execute(
                        """
                        INSERT INTO change_log 
                        (post_id, change_type, old_title, new_title, old_body, new_body, run_time)
                        VALUES (%s, 'MODIFIED', %s, %s, %s, %s, %s)
                        """,
                        (post["id"], old_title, post["title"], old_body, post["body"], RUN_TIME),
                    )

                    # Update latest state in posts table
                    cursor.execute(
                        """
                        UPDATE posts
                        SET userId = %s, title = %s, body = %s
                        WHERE post_id = %s
                        """,
                        (post["userId"], post["title"], post["body"], post["id"]),
                    )

                # Only userId changed
                elif old_user_id != post["userId"]:
                    cursor.execute(
                        "UPDATE posts SET userId = %s WHERE post_id = %s",
                        (post["userId"], post["id"]),
                    )

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Database monitor error: {err}")



# STEP 4: PRINT REPORTS
def print_reports():
    global cursor
    try:
        # 1. POSTS PER USER
        print("\n--- Post Count Per User ---")
        cursor.execute("""
            SELECT userId, COUNT(*) AS post_count
            FROM posts
            GROUP BY userId
            ORDER BY userId DESC
        """)
        for user_id, count in cursor.fetchall():
            print(f"User {user_id}: {count} posts")

        # 2. CHANGE LOG FOR THIS RUN
        print("\n--- Change Log Entries (Latest Run) ---")
        cursor.execute("""
            SELECT log_id, post_id, change_type, old_title, new_title, old_body, new_body, run_time
            FROM change_log
            WHERE run_time >= %s
            ORDER BY log_id DESC
        """, (RUN_TIME,))

        latest_rows = cursor.fetchall()

        if latest_rows:
            for row in latest_rows:
                print(row)
        else:
            print("No changes detected in this run.")

        # 3. USER WITH MOST CHANGES
        print("\n--- User With Most Change Events ---")
        cursor.execute("""
            SELECT p.userId, COUNT(*) AS change_count
            FROM change_log cl
            JOIN posts p ON p.post_id = cl.post_id
            GROUP BY p.userId
            ORDER BY change_count DESC
            LIMIT 1
        """)

        top_user = cursor.fetchone()

        if top_user:
            print(f"User {top_user[0]} with {top_user[1]} change events")
        else:
            print("No change events available.")

    except mysql.connector.Error as err:
        print(f"Report query error: {err}")


# STEP 5: CLOSE CONNECTION
def close_db():
    global conn, cursor
    try:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
    except mysql.connector.Error as err:
        print(f"Error closing database connection: {err}")



if __name__ == "__main__":
    api_data = fetch_data()

    if api_data is None:
        raise SystemExit(1)

    try:
        create_db()
        monitor_posts(api_data)
        print_reports()
    except Exception as err:
        print(f"Unexpected error: {err}")
    finally:
        close_db()