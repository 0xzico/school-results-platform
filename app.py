from flask import Flask, render_template, request, redirect, url_for, flash, session
from math import ceil
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Database connection helper function
def get_db_connection():
    conn = sqlite3.connect('school_results.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user['password_hash']):
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            if user['role'] == 'student':
                return redirect(url_for('student_dashboard'))
            elif user['role'] == 'lecturer':
                return redirect(url_for('lecturer_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
        flash('Invalid email or password!', 'error')
    return render_template('login.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        role = request.form['role']

        # Hash the password
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password_hash, role))
            conn.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
        finally:
            conn.close()
    return render_template('signup.html')

# Logout page
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Student dashboard
@app.route('/student')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    # Fetch results for the logged-in student
    conn = get_db_connection()
    results = conn.execute('''
        SELECT courses.course_name, results.score, results.upload_date
        FROM results
        JOIN courses ON results.course_id = courses.course_id
        WHERE results.student_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('student.html', results=results)

# Lecturer dashboard
@app.route('/lecturer')
def lecturer_dashboard():
    if 'user_id' not in session or session['role'] != 'lecturer':
        flash('Please login as a lecturer to access this page.', 'error')
        return redirect(url_for('login'))

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of results per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    # Fetch total number of results
    total_results = conn.execute('''
        SELECT COUNT(*) FROM results
        WHERE uploaded_by = ?
    ''', (session['user_id'],)).fetchone()[0]

    # Fetch paginated results
    results = conn.execute('''
        SELECT results.result_id, users.name AS student_name, courses.course_name, results.score, results.upload_date
        FROM results
        JOIN users ON results.student_id = users.user_id
        JOIN courses ON results.course_id = courses.course_id
        WHERE results.uploaded_by = ?
        LIMIT ? OFFSET ?
    ''', (session['user_id'], per_page, offset)).fetchall()

    conn.close()

    # Calculate total pages
    total_pages = ceil(total_results / per_page)

    return render_template('lecturer.html', results=results, page=page, total_pages=total_pages)

# Edit result
@app.route('/edit/<int:result_id>', methods=['GET', 'POST'])
def edit_result(result_id):
    if 'user_id' not in session or session['role'] != 'lecturer':
        flash('Please login as a lecturer to access this page.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    result = conn.execute('''
        SELECT results.result_id, users.name AS student_name, courses.course_name, results.score
        FROM results
        JOIN users ON results.student_id = users.user_id
        JOIN courses ON results.course_id = courses.course_id
        WHERE results.result_id = ? AND results.uploaded_by = ?
    ''', (result_id, session['user_id'])).fetchone()

    if request.method == 'POST':
        new_score = request.form['score']
        conn.execute('''
            UPDATE results
            SET score = ?
            WHERE result_id = ?
        ''', (new_score, result_id))
        conn.commit()
        conn.close()
        flash('Result updated successfully!', 'success')
        return redirect(url_for('lecturer_dashboard'))

    conn.close()
    return render_template('edit_result.html', result=result)

# Delete result
@app.route('/delete/<int:result_id>')
def delete_result(result_id):
    if 'user_id' not in session or session['role'] != 'lecturer':
        flash('Please login as a lecturer to access this page.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM results WHERE result_id = ? AND uploaded_by = ?', (result_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Result deleted successfully!', 'success')
    return redirect(url_for('lecturer_dashboard'))

# Admin dashboard
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    return render_template('admin.html')

# File upload and parsing
@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session or session['role'] != 'lecturer':
        flash('Please login as a lecturer to access this page.', 'error')
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file uploaded!', 'error')
        return redirect(url_for('lecturer_dashboard'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('lecturer_dashboard'))

    # Validate file size (e.g., 10 MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    file.seek(0, 2)  # Move to the end of the file
    file_size = file.tell()  # Get the file size
    file.seek(0)  # Reset file pointer to the beginning

    if file_size > MAX_FILE_SIZE:
        flash('File size exceeds the limit (10 MB).', 'error')
        return redirect(url_for('lecturer_dashboard'))

    # Process the file based on its type
    if file.filename.endswith('.csv'):
        import pandas as pd
        try:
            df = pd.read_csv(file)
            # Ensure the CSV has the required columns
            if 'student_id' not in df.columns or 'course_id' not in df.columns or 'score' not in df.columns:
                flash('CSV file must contain columns: student_id, course_id, score', 'error')
                return redirect(url_for('lecturer_dashboard'))
        except Exception as e:
            flash(f'Error reading CSV file: {str(e)}', 'error')
            return redirect(url_for('lecturer_dashboard'))

    elif file.filename.endswith('.pdf'):
        import pdfplumber
        try:
            with pdfplumber.open(file) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text()
            # Parse text (custom logic needed)
            # Example: Assume text is in a specific format
            data = []
            for line in text.split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        student_id = int(parts[0])
                        course_id = int(parts[1])
                        score = float(parts[2])
                        data.append({'student_id': student_id, 'course_id': course_id, 'score': score})
            df = pd.DataFrame(data)
        except Exception as e:
            flash(f'Error reading PDF file: {str(e)}', 'error')
            return redirect(url_for('lecturer_dashboard'))

    else:
        flash('Unsupported file format! Please upload a CSV or PDF file.', 'error')
        return redirect(url_for('lecturer_dashboard'))

    # Save results to the database
    conn = get_db_connection()
    try:
        for _, row in df.iterrows():
            conn.execute('''
                INSERT INTO results (student_id, course_id, score, uploaded_by)
                VALUES (?, ?, ?, ?)
            ''', (row['student_id'], row['course_id'], row['score'], session['user_id']))
        conn.commit()
        flash('File uploaded and results saved successfully!', 'success')
    except Exception as e:
        flash(f'Error saving results to database: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('lecturer_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
