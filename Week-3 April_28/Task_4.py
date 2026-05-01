# Task 04 · Update, Delete & Data Integrity
# Build a student grade management system — insert, update, delete, and validate data

# Create grades.db with a students table: id, name, subject, score, grade TEXT
import mysql.connector

# Function definition to assign grade based on score
def assign_grade(score):
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

conn = None
cursor = None

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='root',                            
        password='root',
    )
    cursor = conn.cursor()

    # Create database and table
    cursor.execute("CREATE DATABASE IF NOT EXISTS grades")
    cursor.execute("USE grades")
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        subject VARCHAR(255) NOT NULL,
                        score INT NOT NULL,
                        grade TEXT
                    )
    """)    

    # Insert 15 students with various scores (mix them between 40–100)
    students = [
        ('Alice', 'Math', 85),
        ('Bob', 'Science', 78),
        ('Charlie', 'History', 92),
        ('David', 'Math', 65),
        ('Eve', 'Science', 55),
        ('Frank', 'History', 48),
        ('Grace', 'Math', 90),
        ('Heidi', 'Science', 82),
        ('Ivan', 'History', 70),
        ('Judy', 'Math', 60),
        ('Karl', 'Science', 45),
        ('Leo', 'History', 88),
        ('Mallory', 'Math', 72),
        ('Nina', 'Science', 80),
        ('Oscar', 'History', 50)
    ] 

    students_with_grades = [
        (name, subject, score, assign_grade(score))
        for name, subject, score in students
    ]

    cursor.executemany("INSERT IGNORE INTO students (name, subject, score, grade) VALUES (%s, %s, %s, %s)", students_with_grades)
    conn.commit()


    # Updating all rows — setting the grade column using the assign_grade function
    cursor.execute("SELECT id, score FROM students")
    for student_id, score in cursor.fetchall():
        grade = assign_grade(score)  # function to assign grade based on score
        cursor.execute("UPDATE students SET grade = %s WHERE id = %s", (grade, student_id))
    conn.commit()
    print("Grade assigned to all students based on their scores successfully.")


    # DELETE all students who scored below 50 — they didn't pass
    cursor.execute("DELETE FROM students WHERE score < %s", (50,))
    conn.commit()

    #Adding a new column "passed" BOOLEAN type using ALTER TABLE — based on score >= 50
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN passed BOOLEAN")
    except mysql.connector.Error:
        pass
    cursor.execute("UPDATE students SET passed = %s WHERE score >= 50", (True,))
    conn.commit()

    # show count of students per grade, ordered from A to F
    cursor.execute("SELECT grade, COUNT(*) FROM students GROUP BY grade ORDER BY FIELD(grade, 'A', 'B', 'C', 'D','E', 'F')")
    grade_counts = cursor.fetchall()
    print("Count of students per grade:")
    for grade, count in grade_counts:
        print(f"{grade}: {count}")


    #Handling the case where a student name is entered twice
    print("\nInsert a new student data in this format (name, subject, score):\n")
    new_student = input()
    parts = [p.strip() for p in new_student.split(',')]
    
    if len(parts) != 3:
        print("Invalid format. Please use: name, subject, score")
    else:
        name, subject, score = parts
        score = int(score)
        grade = assign_grade(score)

        cursor.execute("SELECT COUNT(*) FROM students WHERE name = %s", (name,))
        exists = cursor.fetchone()[0]
        #Adding a new column "passed" BOOLEAN type using ALTER TABLE — based on score >= 50
        if score >= 50:
            passed = True
        else:
            passed = False
            
        if exists == 0:
            cursor.execute(
                "INSERT INTO students (name, subject, score, grade, passed) VALUES (%s, %s, %s, %s, %s)",
                (name, subject, score, grade, passed)
            )
            conn.commit()
            print("New student inserted successfully.")
        else:
            print("Student name already exists. Skipping insert.")
        
except mysql.connector.Error as err:
    print(f"MySQL error: {err}")

finally:
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()
