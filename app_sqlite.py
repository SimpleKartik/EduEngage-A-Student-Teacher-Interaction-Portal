from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here_change_this_in_production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get SQLite database connection"""
    try:
        conn = sqlite3.connect('eduengage.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

def init_database():
    """Initialize database with tables and sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                cabin_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                batch TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cabin_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                UNIQUE(teacher_id, day, time_slot)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_type TEXT NOT NULL,
                team_leader_id INTEGER NOT NULL,
                teacher_id INTEGER,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_leader_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_group_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES project_groups(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(group_id, student_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                guide TEXT,
                description TEXT,
                deadline DATE,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if data exists
        cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cursor.fetchone()[0]
        
        if teacher_count == 0:
            # Add sample data
            teachers_data = [
                ('john.smith', generate_password_hash('pass123'), 'Dr. John Smith', 'Computer Science', 'john.smith@vitbhopal.ac.in'),
                ('sarah.j', generate_password_hash('pass123'), 'Dr. Sarah Johnson', 'Electronics', 'sarah.j@vitbhopal.ac.in'),
                ('michael.b', generate_password_hash('pass123'), 'Prof. Michael Brown', 'Mechanical', 'michael.b@vitbhopal.ac.in')
            ]
            
            students_data = [
                ('alice.c', generate_password_hash('pass123'), 'Alice Cooper', '2024', 'alice.c@vitbhopal.ac.in'),
                ('bob.w', generate_password_hash('pass123'), 'Bob Wilson', '2024', 'bob.w@vitbhopal.ac.in'),
                ('charlie.b', generate_password_hash('pass123'), 'Charlie Brown', '2024', 'charlie.b@vitbhopal.ac.in')
            ]
            
            cursor.executemany("""
                INSERT INTO teachers (username, password, name, department, email)
                VALUES (?, ?, ?, ?, ?)
            """, teachers_data)
            
            cursor.executemany("""
                INSERT INTO students (username, password, name, batch, email)
                VALUES (?, ?, ?, ?, ?)
            """, students_data)
            
            print("Sample data added successfully!")
        
        conn.commit()
        print("Database initialized successfully!")
        
    except sqlite3.Error as err:
        logger.error(f"Database initialization error: {err}")
        raise
    finally:
        cursor.close()
        conn.close()

# Initialize database on startup
init_database()

@app.route('/login/teacher', methods=['POST'])
def teacher_login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Please provide both username and password'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM teachers WHERE username = ?', (username,))
            teacher = cursor.fetchone()
            
            if teacher and check_password_hash(teacher['password'], password):
                session['user_id'] = teacher['id']
                session['user_type'] = 'teacher'
                return jsonify({'success': True, 'redirect': '/teacher_dashboard.html'})
            
            return jsonify({'success': False, 'message': 'Invalid credentials'})
            
        except sqlite3.Error as err:
            logger.error(f"Database error in teacher login: {err}")
            return jsonify({'success': False, 'message': 'Database error occurred. Please try again.'})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Unexpected error in teacher login: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during login. Please try again.'})

@app.route('/login/student', methods=['POST'])
def student_login_submit():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Please provide both username and password'
            })
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM students WHERE username = ?', (username,))
            student = cursor.fetchone()
            
            if student and check_password_hash(student['password'], password):
                session['user_id'] = student['id']
                session['user_type'] = 'student'
                session['username'] = student['username']
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                })
                
        except sqlite3.Error as err:
            logger.error(f"Database error in student login: {err}")
            return jsonify({
                'success': False,
                'message': 'Database error occurred. Please try again.'
            })
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Unexpected error in student login: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during login. Please try again.'
        })

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Add all other routes from your original app.py here...
# (I'm including just the essential ones for now)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teacher_login.html')
def teacher_login_page():
    return render_template('teacher_login.html')

@app.route('/student_login.html')
def student_login_page():
    return render_template('student_login.html')

@app.route('/student_dashboard.html')
def student_dashboard():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect('/student_login.html')
    return render_template('student_dashboard.html')

@app.route('/teacher_dashboard.html')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
