import sqlite3
import bcrypt

# Hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Connect to the database
conn = sqlite3.connect('school_results.db')
cursor = conn.cursor()

# Add sample users
cursor.execute('''
    INSERT INTO users (name, email, password_hash, role)
    VALUES (?, ?, ?, ?)
''', ('John Doe', 'john@example.com', hash_password('password123'), 'student'))

cursor.execute('''
    INSERT INTO users (name, email, password_hash, role)
    VALUES (?, ?, ?, ?)
''', ('Jane Smith', 'jane@example.com', hash_password('password123'), 'lecturer'))

cursor.execute('''
    INSERT INTO users (name, email, password_hash, role)
    VALUES (?, ?, ?, ?)
''', ('Admin', 'admin@example.com', hash_password('admin123'), 'admin'))

# Add sample courses
cursor.execute('''
    INSERT INTO courses (course_name, lecturer_id)
    VALUES (?, ?)
''', ('Mathematics', 2))

cursor.execute('''
    INSERT INTO courses (course_name, lecturer_id)
    VALUES (?, ?)
''', ('Physics', 2))

# Add sample enrollments
cursor.execute('''
    INSERT INTO enrollments (student_id, course_id)
    VALUES (?, ?)
''', (1, 1))

cursor.execute('''
    INSERT INTO enrollments (student_id, course_id)
    VALUES (?, ?)
''', (1, 2))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Sample data added successfully!")