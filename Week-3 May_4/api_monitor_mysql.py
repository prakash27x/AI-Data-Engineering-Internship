# Task B · API Monitor with Change Detection [Hard]

import json
import random
import mysql.connector
from urllib.request import urlopen


BASE_URL = "https://jsonplaceholder.typicode.com/posts"
RUN_ID = random.randint(100000, 999999)
conn = None
cursor = None


def fetch_data():
    try:
        response = urlopen(BASE_URL)
        return json.loads(response.read())
    except Exception as err:
        print(f"Error fetching API data: {err}")
        return None


def create_db():
    global conn, cursor
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root")
        cursor = conn.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS monitor_db")
        cursor.execute("USE monitor_db")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                post_id INT PRIMARY KEY,
                userId INT,
                title VARCHAR(255),
                body TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS change_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                post_id INT,
                change_type VARCHAR(20),
                old_title VARCHAR(255),
                new_title VARCHAR(255),
                old_body TEXT,
                new_body TEXT,
                run_id INT,
                changed_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(post_id)
            )
            """
        )

        # Backward-compatible migration for tables created before run_id existed.
        cursor.execute("SHOW COLUMNS FROM change_log LIKE 'run_id'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE change_log ADD COLUMN run_id INT NULL")

        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database setup error: {err}")


def monitor_posts(api_posts):
    global conn, cursor
    try:
        for post in api_posts:
            cursor.execute(
                "SELECT userId, title, body FROM posts WHERE post_id = %s",
                (post["id"],),
            )
            existing = cursor.fetchone()

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
                    INSERT INTO change_log (post_id, change_type, old_title, new_title, old_body, new_body, run_id)
                    VALUES (%s, 'NEW', NULL, %s, NULL, %s, %s)
                    """,
                    (post["id"], post["title"], post["body"], RUN_ID),
                )
            else:
                old_user_id, old_title, old_body = existing
                if old_title != post["title"] or old_body != post["body"]:
                    cursor.execute(
                        """
                        INSERT INTO change_log (post_id, change_type, old_title, new_title, old_body, new_body, run_id)
                        VALUES (%s, 'MODIFIED', %s, %s, %s, %s, %s)
                        """,
                        (post["id"], old_title, post["title"], old_body, post["body"], RUN_ID),
                    )
                    cursor.execute(
                        """
                        UPDATE posts
                        SET userId = %s, title = %s, body = %s
                        WHERE post_id = %s
                        """,
                        (post["userId"], post["title"], post["body"], post["id"]),
                    )
                elif old_user_id != post["userId"]:
                    cursor.execute(
                        "UPDATE posts SET userId = %s WHERE post_id = %s",
                        (post["userId"], post["id"]),
                    )

        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database monitor error: {err}")


def print_reports():
    global cursor
    try:
        print("\n--- Post Count Per User ---")
        cursor.execute(
            """
            SELECT userId, COUNT(*) AS post_count
            FROM posts
            GROUP BY userId
            ORDER BY userId
            """
        )
        for user_id, count in cursor.fetchall():
            print(f"User {user_id}: {count} posts")

        print("\n--- Change Log Entries (Latest Run) ---")
        cursor.execute(
            """
            SELECT log_id, post_id, change_type, old_title, new_title, changed_time
            FROM change_log
            WHERE run_id = %s
            ORDER BY log_id
            """,
            (RUN_ID,),
        )
        latest_rows = cursor.fetchall()
        if latest_rows:
            for row in latest_rows:
                print(row)
        else:
            print("No changes detected in this run.")

        print("\n--- User With Most Change Events ---")
        cursor.execute(
            """
            SELECT p.userId, COUNT(*) AS change_count
            FROM change_log cl
            JOIN posts p ON p.post_id = cl.post_id
            GROUP BY p.userId
            ORDER BY change_count DESC
            LIMIT 1
            """
        )
        top_user = cursor.fetchone()
        if top_user:
            print(f"User {top_user[0]} with {top_user[1]} change events")
        else:
            print("No change events available.")
    except mysql.connector.Error as err:
        print(f"Report query error: {err}")


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