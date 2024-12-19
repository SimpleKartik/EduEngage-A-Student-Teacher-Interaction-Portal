from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

def get_db_connection():
    return mysql.connector.connect(
        host='sql12.freemysqlhosting.net',
        user='sql12752768',
        password='III99fbDnZ',
        database='sql12752768'
    )

@app.route('/login/teacher', methods=['POST'])
def teacher_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM teachers WHERE username = %s', (username,))
    teacher = cursor.fetchone()
    
    if teacher and check_password_hash(teacher['password'], password):
        session['user_id'] = teacher['id']
        session['user_type'] = 'teacher'
        return jsonify({'success': True, 'redirect': '/teacher_dashboard.html'})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/login/student', methods=['POST'])
def student_login_submit():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'message': 'Please provide both username and password'
        })
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            'SELECT * FROM students WHERE username = %s',
            (username,)
        )
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
            
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during login'
        })
        
    finally:
        cursor.close()
        conn.close()

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
            INSERT INTO cabin_status (teacher_id, day, time_slot, status)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status = %s
        """, (teacher_id, day, time_slot, status, status))
        
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
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT cs.*, t.name as teacher_name, t.department
        FROM cabin_status cs
        JOIN teachers t ON cs.teacher_id = t.id
        WHERE cs.teacher_id = %s
    """, (teacher_id,))
    
    status = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(status)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/project_info.html')
def project_info():
    return render_template('project_info.html')

@app.route('/get_cabin_status', methods=['GET'])
def get_cabin_status():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cabin_status")
    status = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(status)

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
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT day, time_slot, status 
            FROM cabin_status 
            WHERE teacher_id = %s
        """, (teacher_id,))
        
        status = cursor.fetchall()
        return jsonify(status)
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
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT id, name, department 
            FROM teachers 
            ORDER BY name
        ''')
        
        faculty = cursor.fetchall()
        return jsonify(faculty)
        
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
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT day, time_slot, status 
            FROM cabin_status 
            WHERE teacher_id = %s
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
        return jsonify(status)
        
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
    cursor = conn.cursor(dictionary=True)
    
    try:
        # First get the teacher's ID
        cursor.execute('SELECT id FROM teachers WHERE name = %s', (teacher_name,))
        teacher = cursor.fetchone()
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
            
        # Get the cabin status for this teacher
        cursor.execute('''
            SELECT day, time_slot, status 
            FROM cabin_status 
            WHERE teacher_id = %s
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
        return jsonify(status)
        
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
    cursor = conn.cursor(dictionary=True)
    
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
        return jsonify(projects)
        
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
    cursor = conn.cursor(dictionary=True)
    
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
        return jsonify(students)
        
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
        cursor.execute("START TRANSACTION")
        
        # Create project group
        cursor.execute('''
            INSERT INTO project_groups (project_type, team_leader_id, status)
            VALUES (%s, %s, 'pending')
        ''', (project_type, team_leader_id))
        
        group_id = cursor.lastrowid
        
        # Add members to group
        for student_id in members:
            cursor.execute('''
                INSERT INTO project_group_members (group_id, student_id)
                VALUES (%s, %s)
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
    cursor = conn.cursor(dictionary=True)
    
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
                WHERE pgm.student_id = %s
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
                WHERE pg.teacher_id = %s
                GROUP BY pg.id
            ''', (session['user_id'],))
        
        projects = cursor.fetchall()
        return jsonify(projects)
        
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
            SET status = %s 
            WHERE id = %s AND teacher_id = %s
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
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT 
                pg.id,
                pg.project_type,
                pg.status,
                t.name as teacher_name,
                (
                    SELECT JSON_ARRAYAGG(
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
            WHERE pgm.student_id = %s
        ''', (session['user_id'],))
        
        groups = cursor.fetchall()
        
        # Parse the JSON string for members
        for group in groups:
            if group['members']:
                group['members'] = json.loads(group['members'])
            else:
                group['members'] = []
                
        return jsonify(groups)
        
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
    cursor = conn.cursor(dictionary=True)
    
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
            WHERE pgm.student_id = %s
            GROUP BY pg.id
        ''', (session['user_id'],))
        
        groups = cursor.fetchall()
        return jsonify(groups)
        
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
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get count of groups already assigned to this teacher
        cursor.execute('''
            SELECT COUNT(*) as group_count 
            FROM project_groups 
            WHERE teacher_id = %s
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
            WHERE pg.teacher_id = %s
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
            'current_groups': current_groups,
            'available_groups': available_groups
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
            WHERE teacher_id = %s
        ''', (session['user_id'],))
        
        if cursor.fetchone()[0] >= 5:
            return jsonify({
                'success': False,
                'message': 'You have reached the maximum limit of 5 groups'
            }), 400
            
        # Assign group to teacher
        cursor.execute('''
            UPDATE project_groups 
            SET teacher_id = %s, 
                status = 'ongoing'
            WHERE id = %s AND teacher_id IS NULL
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
    cursor = conn.cursor(dictionary=True)
    
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
            AND cs.day = DATE_FORMAT(NOW(), '%W')
            AND cs.time_slot = (
                SELECT time_slot 
                FROM cabin_status 
                WHERE TIME(NOW()) BETWEEN 
                    STR_TO_DATE(time_slot, '%l:%i %p') 
                    AND ADDTIME(STR_TO_DATE(time_slot, '%l:%i %p'), '01:35:00')
                LIMIT 1
            )
            ORDER BY t.name
        ''')
        
        faculty = cursor.fetchall()
        return jsonify(faculty)
        
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
    cursor = conn.cursor(dictionary=True)
    
    try:
        # First get all teachers
        cursor.execute('''
            SELECT 
                t.id,
                t.name,
                t.department,
                t.email,
                t.cabin_number
            FROM teachers t
            ORDER BY t.name
        ''')
        
        teachers = cursor.fetchall()
        
        # Then get their schedules
        for teacher in teachers:
            cursor.execute('''
                SELECT 
                    day,
                    time_slot,
                    status
                FROM cabin_status
                WHERE teacher_id = %s
                ORDER BY 
                    FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'),
                    time_slot
            ''', (teacher['id'],))
            
            schedule = cursor.fetchall()
            
            # Organize schedule by day and time
            teacher_schedule = {
                'Monday': {}, 'Tuesday': {}, 'Wednesday': {}, 
                'Thursday': {}, 'Friday': {}
            }
            
            for slot in schedule:
                teacher_schedule[slot['day']][slot['time_slot']] = slot['status']
            
            teacher['schedule'] = teacher_schedule
            del teacher['id']  # Remove ID from response
        
        return jsonify(teachers)
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': 'Failed to fetch faculty data'}), 500
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host=0.0.0.0)
