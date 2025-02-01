import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('school_results.db')
cursor = conn.cursor()

# Create Users Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Create Courses Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        lecturer_id INTEGER,
        FOREIGN KEY (lecturer_id) REFERENCES users (user_id)
    )
''')

# Create Results Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        score REAL,
        uploaded_by INTEGER,
        upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users (user_id),
        FOREIGN KEY (course_id) REFERENCES courses (course_id),
        FOREIGN KEY (uploaded_by) REFERENCES users (user_id)
    )
''')

# Create Enrollments Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        FOREIGN KEY (student_id) REFERENCES users (user_id),
        FOREIGN KEY (course_id) REFERENCES courses (course_id)
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully!")