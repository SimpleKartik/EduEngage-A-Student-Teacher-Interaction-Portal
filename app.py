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
            
            # Add sample cabin status data
            cursor.execute("SELECT id FROM teachers")
            teacher_ids = [row[0] for row in cursor.fetchall()]
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            time_slots = ['8:30 AM', '10:05 AM', '11:40 AM', '1:15 PM', '2:50 PM', '4:25 PM', '6:00 PM']
            
            for teacher_id in teacher_ids:
                for day in days:
                    for time_slot in time_slots:
                        cursor.execute("""
                            INSERT INTO cabin_status (teacher_id, day, time_slot, status)
                            VALUES (?, ?, ?, ?)
                        """, (teacher_id, day, time_slot, 'Available'))
            
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

@app.route('/update_cabin_status', methods=['POST'])
def update_cabin_status():
    if 'user_id' not in session or session['user_type'] != 'teacher':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    teacher_id = session['user_id']
    day = data['day']
    time_slot = data['time_slot']
    status = data['status']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO cabin_status (teacher_id, day, time_slot, status)
            VALUES (?, ?, ?, ?)
        """, (teacher_id, day, time_slot, status))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Status updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/get_teacher_status/<int:teacher_id>')
def get_teacher_status(teacher_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cs.*, t.name as teacher_name, t.department
        FROM cabin_status cs
        JOIN teachers t ON cs.teacher_id = t.id
        WHERE cs.teacher_id = ?
    """, (teacher_id,))
    
    status = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify([dict(row) for row in status])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/project_info.html')
def project_info():
    return render_template('project_info.html')

@app.route('/get_cabin_status', methods=['GET'])
def get_cabin_status():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cabin_status")
    status = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify([dict(row) for row in status])

@app.route('/epix_project.html')
def epix_project():
    return render_template('epix_project.html')

@app.route('/project_exhibition.html')
def project_exhibition():
    return render_template('project_exhibition.html')

@app.route('/capstone_project.html')
def capstone_project():
    return render_template('capstone_project.html')

@app.route('/student_dashboard.html')
def student_dashboard():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect('/student_login.html')
    return render_template('student_dashboard.html')

@app.route('/teacher_dashboard.html')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

@app.route('/create_group.html')
def create_group():
    return render_template('create_group.html')

@app.route('/create_group_capstone.html')
def create_group_capstone():
    return render_template('create_group_capstone.html')

@app.route('/create_group_epics.html')
def create_group_epics():
    return render_template('create_group_epics.html')

@app.route('/view_group.html')
def view_group():
    return render_template('view_group.html')

@app.route('/search_faculty.html')
def search_faculty_page():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('student_login'))
    return render_template('search_faculty.html')

@app.route('/cabin_status.html')
def cabin_status():
    return render_template('cabin_status.html')

@app.route('/update_cabin_status')
def update_cabin_status_page():
    return render_template('update_cabin_status.html')

@app.route('/teacher_login.html')
def teacher_login_page():
    return render_template('teacher_login.html')

@app.route('/student_login.html')
def student_login_page():
    return render_template('student_login.html')

@app.route('/get_teacher_cabin_status')
def get_teacher_cabin_status():
    if 'user_id' not in session or session['user_type'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
    
    teacher_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT day, time_slot, status 
            FROM cabin_status 
            WHERE teacher_id = ?
        """, (teacher_id,))
        
        status = cursor.fetchall()
        return jsonify([dict(row) for row in status])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Add this route to protect the student dashboard
@app.before_request
def check_student_auth():
    protected_routes = ['/student_dashboard.html', '/search_faculty.html', '/project_info.html']
    if request.path in protected_routes:
        if 'user_id' not in session or session['user_type'] != 'student':
            return redirect('/student_login.html')

@app.route('/project_info.html')
def project_info_page():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('student_login'))
    return render_template('project_info.html')

@app.route('/api/faculty/list')
def get_faculty_list():
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, name, department 
            FROM teachers 
            ORDER BY name
        ''')
        
        faculty = cursor.fetchall()
        return jsonify([dict(row) for row in faculty])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch faculty data'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/view_cabin_status')
def view_cabin_status():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('student_login'))
        
    faculty_name = request.args.get('name')
    department = request.args.get('department')
    
    return render_template('view_cabin_status.html', 
                         faculty_name=faculty_name, 
                         department=department)

@app.route('/api/faculty/cabin-status/<int:teacher_id>')
def get_faculty_cabin_status(teacher_id):
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT day, time_slot, status 
            FROM cabin_status 
            WHERE teacher_id = ?
            ORDER BY 
                CASE day 
                    WHEN 'Monday' THEN 1 
                    WHEN 'Tuesday' THEN 2 
                    WHEN 'Wednesday' THEN 3 
                    WHEN 'Thursday' THEN 4 
                    WHEN 'Friday' THEN 5 
                END,
                time_slot
        ''', (teacher_id,))
        
        status = cursor.fetchall()
        return jsonify([dict(row) for row in status])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch cabin status'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/faculty/status/view/<teacher_name>')
def get_teacher_status_view(teacher_name):
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First get the teacher's ID
        cursor.execute('SELECT id FROM teachers WHERE name = ?', (teacher_name,))
        teacher = cursor.fetchone()
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
            
        # Get the cabin status for this teacher
        cursor.execute('''
            SELECT day, time_slot, status 
            FROM cabin_status 
            WHERE teacher_id = ?
            ORDER BY 
                CASE day
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                END,
                time_slot
        ''', (teacher['id'],))
        
        status = cursor.fetchall()
        return jsonify([dict(row) for row in status])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch cabin status'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/projects')
def get_projects():
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                title,
                guide,
                description,
                deadline,
                status
            FROM projects
            ORDER BY deadline ASC
        ''')
        
        projects = cursor.fetchall()
        return jsonify([dict(row) for row in projects])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch projects'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/available-students')
def get_available_students():
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get students who aren't already in a project group of the same type
        cursor.execute('''
            SELECT s.id, s.name, s.batch 
            FROM students s
            WHERE s.id NOT IN (
                SELECT pgm.student_id 
                FROM project_group_members pgm
                JOIN project_groups pg ON pgm.group_id = pg.id
                WHERE pg.status != 'completed'
            )
            ORDER BY s.name
        ''')
        
        students = cursor.fetchall()
        return jsonify([dict(row) for row in students])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch available students'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/create-project-group', methods=['POST'])
def create_project_group():
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    project_type = data.get('projectType')
    team_leader_id = data.get('teamLeaderId')
    members = data.get('members', [])
    
    if len(members) > 5:
        return jsonify({
            'success': False,
            'message': 'Maximum 5 students allowed in a group'
        }), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create project group
        cursor.execute('''
            INSERT INTO project_groups (project_type, team_leader_id, status)
            VALUES (?, ?, 'pending')
        ''', (project_type, team_leader_id))
        
        group_id = cursor.lastrowid
        
        # Add members to group
        for student_id in members:
            cursor.execute('''
                INSERT INTO project_group_members (group_id, student_id)
                VALUES (?, ?)
            ''', (group_id, student_id))
        
        # Commit transaction
        cursor.execute("COMMIT")
        
        return jsonify({
            'success': True,
            'message': 'Project group created successfully'
        })
        
    except Exception as e:
        # Rollback in case of error
        cursor.execute("ROLLBACK")
        print(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create project group'
        }), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/current-projects')
def get_current_projects():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if session['user_type'] == 'student':
            # Get projects where the student is a member
            cursor.execute('''
                SELECT 
                    pg.id,
                    pg.project_type,
                    pg.status,
                    pg.created_at,
                    t.name as teacher_name,
                    s.name as team_leader_name,
                    GROUP_CONCAT(sm.name) as member_names
                FROM project_groups pg
                JOIN project_group_members pgm ON pg.id = pgm.group_id
                JOIN students s ON pg.team_leader_id = s.id
                LEFT JOIN teachers t ON pg.teacher_id = t.id
                JOIN project_group_members pgm2 ON pg.id = pgm2.group_id
                JOIN students sm ON pgm2.student_id = sm.id
                WHERE pgm.student_id = ?
                GROUP BY pg.id
            ''', (session['user_id'],))
        else:  # teacher
            # Get projects assigned to this teacher
            cursor.execute('''
                SELECT 
                    pg.id,
                    pg.project_type,
                    pg.status,
                    pg.created_at,
                    s.name as team_leader_name,
                    GROUP_CONCAT(sm.name) as member_names
                FROM project_groups pg
                JOIN students s ON pg.team_leader_id = s.id
                JOIN project_group_members pgm ON pg.id = pgm.group_id
                JOIN students sm ON pgm.student_id = sm.id
                WHERE pg.teacher_id = ?
                GROUP BY pg.id
            ''', (session['user_id'],))
        
        projects = cursor.fetchall()
        return jsonify([dict(row) for row in projects])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch projects'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/update-project-status', methods=['POST'])
def update_project_status():
    if 'user_id' not in session or session['user_type'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    project_id = data.get('projectId')
    new_status = data.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE project_groups 
            SET status = ? 
            WHERE id = ? AND teacher_id = ?
        ''', (new_status, project_id, session['user_id']))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Project status updated successfully'
        })
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update project status'
        }), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/teacher_projects')
def teacher_projects():
    if 'user_id' not in session or session['user_type'] != 'teacher':
        return redirect(url_for('teacher_login'))
    return render_template('teacher_projects.html')

@app.route('/api/my-groups')
def get_my_groups():
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                pg.id,
                pg.project_type,
                pg.status,
                t.name as teacher_name,
                (
                    SELECT JSON_GROUP_ARRAY(
                        JSON_OBJECT(
                            'name', s.name,
                            'is_leader', s.id = pg.team_leader_id
                        )
                    )
                    FROM project_group_members pgm2
                    JOIN students s ON pgm2.student_id = s.id
                    WHERE pgm2.group_id = pg.id
                ) as members
            FROM project_groups pg
            JOIN project_group_members pgm ON pg.id = pgm.group_id
            LEFT JOIN teachers t ON pg.teacher_id = t.id
            WHERE pgm.student_id = ?
        ''', (session['user_id'],))
        
        groups = cursor.fetchall()
        
        # Parse the JSON string for members
        for group in groups:
            if group['members']:
                group['members'] = json.loads(group['members'])
            else:
                group['members'] = []
                
        return jsonify([dict(row) for row in groups])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch groups'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/student_groups')
def student_groups():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('student_login'))
    return render_template('student_groups.html')

@app.route('/api/student/groups')
def get_student_groups():
    if 'user_id' not in session or session['user_type'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                pg.id,
                pg.project_type,
                pg.status,
                t.name as teacher_name,
                s.name as team_leader_name,
                GROUP_CONCAT(sm.name) as member_names
            FROM project_groups pg
            JOIN project_group_members pgm ON pg.id = pgm.group_id
            JOIN students s ON pg.team_leader_id = s.id
            LEFT JOIN teachers t ON pg.teacher_id = t.id
            JOIN project_group_members pgm2 ON pg.id = pgm2.group_id
            JOIN students sm ON pgm2.student_id = sm.id
            WHERE pgm.student_id = ?
            GROUP BY pg.id
        ''', (session['user_id'],))
        
        groups = cursor.fetchall()
        return jsonify([dict(row) for row in groups])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch groups'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/teacher_group_selection')
def teacher_group_selection():
    if 'user_id' not in session or session['user_type'] != 'teacher':
        return redirect(url_for('teacher_login'))
    return render_template('teacher_group_selection.html')

@app.route('/api/teacher/available-groups')
def get_available_groups():
    if 'user_id' not in session or session['user_type'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get count of groups already assigned to this teacher
        cursor.execute('''
            SELECT COUNT(*) as group_count 
            FROM project_groups 
            WHERE teacher_id = ?
        ''', (session['user_id'],))
        
        result = cursor.fetchone()
        current_groups = result['group_count']
        
        if current_groups >= 5:
            return jsonify({
                'error': 'Maximum groups limit reached',
                'current_groups': [],
                'available_groups': []
            })
        
        # Get currently assigned groups
        cursor.execute('''
            SELECT 
                pg.id,
                pg.project_type,
                pg.status,
                s.name as team_leader_name,
                GROUP_CONCAT(sm.name) as member_names,
                COUNT(pgm.student_id) as team_size
            FROM project_groups pg
            JOIN students s ON pg.team_leader_id = s.id
            JOIN project_group_members pgm ON pg.id = pgm.group_id
            JOIN students sm ON pgm.student_id = sm.id
            WHERE pg.teacher_id = ?
            GROUP BY pg.id
        ''', (session['user_id'],))
        
        current_groups = cursor.fetchall()
        
        # Get available groups (not assigned to any teacher)
        cursor.execute('''
            SELECT 
                pg.id,
                pg.project_type,
                pg.status,
                s.name as team_leader_name,
                GROUP_CONCAT(sm.name) as member_names,
                COUNT(pgm.student_id) as team_size
            FROM project_groups pg
            JOIN students s ON pg.team_leader_id = s.id
            JOIN project_group_members pgm ON pg.id = pgm.group_id
            JOIN students sm ON pgm.student_id = sm.id
            WHERE pg.teacher_id IS NULL
            GROUP BY pg.id
        ''')
        
        available_groups = cursor.fetchall()
        
        return jsonify({
            'current_groups': [dict(row) for row in current_groups],
            'available_groups': [dict(row) for row in available_groups]
        })
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch groups'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/teacher/select-group', methods=['POST'])
def select_group():
    if 'user_id' not in session or session['user_type'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
        
    group_id = request.json.get('group_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check current group count
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM project_groups 
            WHERE teacher_id = ?
        ''', (session['user_id'],))
        
        if cursor.fetchone()[0] >= 5:
            return jsonify({
                'success': False,
                'message': 'You have reached the maximum limit of 5 groups'
            }), 400
            
        # Assign group to teacher
        cursor.execute('''
            UPDATE project_groups 
            SET teacher_id = ?, 
                status = 'ongoing'
            WHERE id = ? AND teacher_id IS NULL
        ''', (session['user_id'], group_id))
        
        if cursor.rowcount == 0:
            return jsonify({
                'success': False,
                'message': 'Group is no longer available'
            }), 400
            
        conn.commit()
        return jsonify({
            'success': True,
            'message': 'Group assigned successfully'
        })
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        conn.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to assign group'
        }), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/faculty')
def get_faculty():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                t.name,
                t.department,
                t.email,
                t.cabin_number,
                COALESCE(cs.status, 'Not-Available') as current_status
            FROM teachers t
            LEFT JOIN cabin_status cs ON t.id = cs.teacher_id
            AND cs.day = strftime('%W', 'now')
            AND cs.time_slot = (
                SELECT time_slot 
                FROM cabin_status 
                WHERE time('now') BETWEEN 
                    time(time_slot) 
                    AND time(time_slot, '+1 hour', '+35 minutes')
                LIMIT 1
            )
            ORDER BY t.name
        ''')
        
        faculty = cursor.fetchall()
        return jsonify([dict(row) for row in faculty])
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch faculty data'}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/faculty/schedule')
def get_faculty_schedule():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all teachers with basic info
        cursor.execute('''
            SELECT 
                t.id,
                t.name,
                t.department,
                t.email,
                COALESCE(t.cabin_number, 'TBD') as cabin_number
            FROM teachers t
            ORDER BY t.name
        ''')
        
        teachers = cursor.fetchall()
        
        # Convert to list of dictionaries
        faculty_list = []
        for teacher in teachers:
            teacher_dict = dict(teacher)
            
            # Get schedule for this teacher
            cursor.execute('''
                SELECT 
                    day,
                    time_slot,
                    status
                FROM cabin_status
                WHERE teacher_id = ?
                ORDER BY 
                    CASE day
                        WHEN 'Monday' THEN 1
                        WHEN 'Tuesday' THEN 2
                        WHEN 'Wednesday' THEN 3
                        WHEN 'Thursday' THEN 4
                        WHEN 'Friday' THEN 5
                    END,
                    time_slot
            ''', (teacher_dict['id'],))
            
            schedule_data = cursor.fetchall()
            
            # Organize schedule by day and time
            teacher_schedule = {
                'Monday': {}, 'Tuesday': {}, 'Wednesday': {}, 
                'Thursday': {}, 'Friday': {}
            }
            
            for slot in schedule_data:
                teacher_schedule[slot['day']][slot['time_slot']] = slot['status']
            
            # Add default schedule if no data exists
            time_slots = ['8:30 AM', '10:05 AM', '11:40 AM', '1:15 PM', '2:50 PM', '4:25 PM', '6:00 PM']
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                for time_slot in time_slots:
                    if time_slot not in teacher_schedule[day]:
                        teacher_schedule[day][time_slot] = 'Available'
            
            teacher_dict['schedule'] = teacher_schedule
            del teacher_dict['id']  # Remove ID from response
            faculty_list.append(teacher_dict)
        
        return jsonify(faculty_list)
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch faculty data'}), 500
        
    finally:
        cursor.close()
        conn.close()

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

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
