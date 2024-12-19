import mysql.connector
from werkzeug.security import generate_password_hash
import csv
from datetime import datetime, timedelta

def get_db_connection():
    return mysql.connector.connect(
        host='sql12.freemysqlhosting.net',
        user='sql12752768',
        password='III99fbDnZ',
        database='sql12752768'
    )

def create_initial_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM cabin_status")
    cursor.execute("DELETE FROM project_group_members")
    cursor.execute("DELETE FROM project_groups")
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM teachers")
    
    # Create teachers
    teachers_data = [
        ('Dr. John Smith', 'Computer Science', 'john.smith', 'pass123', 'john.smith@vitbhopal.ac.in'),
        ('Dr. Sarah Johnson', 'Electronics', 'sarah.j', 'pass123', 'sarah.j@vitbhopal.ac.in'),
        ('Prof. Michael Brown', 'Mechanical', 'michael.b', 'pass123', 'michael.b@vitbhopal.ac.in'),
        ('Dr. Emily Davis', 'Computer Science', 'emily.d', 'pass123', 'emily.d@vitbhopal.ac.in'),
        ('Prof. Robert Wilson', 'Electronics', 'robert.w', 'pass123', 'robert.w@vitbhopal.ac.in')
    ]

    # Create students
    students_data = [
        ('Alice Cooper', '2024', 'alice.c', 'pass123', 'alice.c@vitbhopal.ac.in'),
        ('Bob Wilson', '2024', 'bob.w', 'pass123', 'bob.w@vitbhopal.ac.in'),
        ('Charlie Brown', '2024', 'charlie.b', 'pass123', 'charlie.b@vitbhopal.ac.in'),
        ('David Miller', '2024', 'david.m', 'pass123', 'david.m@vitbhopal.ac.in'),
        ('Eva Garcia', '2024', 'eva.g', 'pass123', 'eva.g@vitbhopal.ac.in'),
        ('Frank Lee', '2024', 'frank.l', 'pass123', 'frank.l@vitbhopal.ac.in'),
        ('Grace Kim', '2024', 'grace.k', 'pass123', 'grace.k@vitbhopal.ac.in'),
        ('Henry Patel', '2024', 'henry.p', 'pass123', 'henry.p@vitbhopal.ac.in'),
        ('Ivy Chen', '2024', 'ivy.c', 'pass123', 'ivy.c@vitbhopal.ac.in'),
        ('Jack Thompson', '2024', 'jack.t', 'pass123', 'jack.t@vitbhopal.ac.in')
    ]

    # Save login credentials to CSV
    with open('login_credentials.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Type', 'Name', 'Username', 'Password', 'Email'])
        
        # Add teachers
        for name, dept, username, password, email in teachers_data:
            try:
                cursor.execute('''
                    INSERT INTO teachers (name, department, username, password, email) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (name, dept, username, generate_password_hash(password), email))
                writer.writerow(['Teacher', name, username, password, email])
            except Exception as e:
                print(f"Error adding teacher {name}: {str(e)}")

        # Add students
        for name, batch, username, password, email in students_data:
            try:
                cursor.execute('''
                    INSERT INTO students (name, batch, username, password, email) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (name, batch, username, generate_password_hash(password), email))
                writer.writerow(['Student', name, username, password, email])
            except Exception as e:
                print(f"Error adding student {name}: {str(e)}")

    # Create some initial cabin status entries
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_slots = ['8:30 AM', '10:05 AM', '11:40 AM', '1:15 PM', '2:50 PM', '4:25 PM', '6:00 PM']
    
    cursor.execute('SELECT id FROM teachers')
    teacher_ids = [row[0] for row in cursor.fetchall()]

    # Delete existing cabin status entries
    cursor.execute('DELETE FROM cabin_status')

    # Insert new cabin status entries
    for teacher_id in teacher_ids:
        for day in days:
            for time_slot in time_slots:
                try:
                    cursor.execute('''
                        INSERT INTO cabin_status (teacher_id, day, time_slot, status)
                        VALUES (%s, %s, %s, %s)
                    ''', (teacher_id, day, time_slot, 'Available'))
                except Exception as e:
                    print(f"Error adding cabin status for teacher {teacher_id}, {day}, {time_slot}: {str(e)}")

    conn.commit()
    cursor.close()
    conn.close()

    print("Initial data created successfully!")
    print("Login credentials have been saved to login_credentials.csv")

if __name__ == "__main__":
    create_initial_data() 