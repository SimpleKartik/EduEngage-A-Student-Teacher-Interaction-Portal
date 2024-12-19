import mysql.connector
from werkzeug.security import generate_password_hash
import csv
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host='sql12.freemysqlhosting.net',
        user='sql12752768',
        password='III99fbDnZ',
        database='sql12752768'
    )

def add_more_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Additional teachers data
    new_teachers = [
        ('Dr. Lisa Chen', 'Computer Science', 'lisa.chen', 'pass123', 'lisa.chen@vitbhopal.ac.in'),
        ('Prof. David Kumar', 'Electronics', 'david.k', 'pass123', 'david.k@vitbhopal.ac.in'),
        ('Dr. Maria Rodriguez', 'Mechanical', 'maria.r', 'pass123', 'maria.r@vitbhopal.ac.in'),
        ('Prof. Raj Patel', 'Computer Science', 'raj.p', 'pass123', 'raj.p@vitbhopal.ac.in'),
        ('Dr. Amanda White', 'Electronics', 'amanda.w', 'pass123', 'amanda.w@vitbhopal.ac.in')
    ]

    # Additional students data
    new_students = [
        ('Rahul Sharma', '2024', 'rahul.s', 'pass123', 'rahul.s@vitbhopal.ac.in'),
        ('Priya Patel', '2024', 'priya.p', 'pass123', 'priya.p@vitbhopal.ac.in'),
        ('Amit Kumar', '2024', 'amit.k', 'pass123', 'amit.k@vitbhopal.ac.in'),
        ('Neha Singh', '2024', 'neha.s', 'pass123', 'neha.s@vitbhopal.ac.in'),
        ('Raj Malhotra', '2024', 'raj.m', 'pass123', 'raj.m@vitbhopal.ac.in'),
        ('Ananya Gupta', '2024', 'ananya.g', 'pass123', 'ananya.g@vitbhopal.ac.in'),
        ('Vikram Verma', '2024', 'vikram.v', 'pass123', 'vikram.v@vitbhopal.ac.in'),
        ('Pooja Shah', '2024', 'pooja.s', 'pass123', 'pooja.s@vitbhopal.ac.in'),
        ('Arjun Reddy', '2024', 'arjun.r', 'pass123', 'arjun.r@vitbhopal.ac.in'),
        ('Meera Kapoor', '2024', 'meera.k', 'pass123', 'meera.k@vitbhopal.ac.in'),
        ('Aditya Joshi', '2024', 'aditya.j', 'pass123', 'aditya.j@vitbhopal.ac.in'),
        ('Riya Desai', '2024', 'riya.d', 'pass123', 'riya.d@vitbhopal.ac.in'),
        ('Kunal Mehta', '2024', 'kunal.m', 'pass123', 'kunal.m@vitbhopal.ac.in'),
        ('Shreya Sinha', '2024', 'shreya.s', 'pass123', 'shreya.s@vitbhopal.ac.in'),
        ('Rohan Khanna', '2024', 'rohan.k', 'pass123', 'rohan.k@vitbhopal.ac.in'),
        ('Nisha Patel', '2024', 'nisha.p', 'pass123', 'nisha.p@vitbhopal.ac.in'),
        ('Varun Singh', '2024', 'varun.s', 'pass123', 'varun.s@vitbhopal.ac.in'),
        ('Anjali Sharma', '2024', 'anjali.s', 'pass123', 'anjali.s@vitbhopal.ac.in'),
        ('Karan Malhotra', '2024', 'karan.m', 'pass123', 'karan.m@vitbhopal.ac.in'),
        ('Divya Gupta', '2024', 'divya.g', 'pass123', 'divya.g@vitbhopal.ac.in'),
        ('Siddharth Roy', '2024', 'siddharth.r', 'pass123', 'siddharth.r@vitbhopal.ac.in'),
        ('Tanvi Desai', '2024', 'tanvi.d', 'pass123', 'tanvi.d@vitbhopal.ac.in'),
        ('Aryan Kapoor', '2024', 'aryan.k', 'pass123', 'aryan.k@vitbhopal.ac.in'),
        ('Ishaan Verma', '2024', 'ishaan.v', 'pass123', 'ishaan.v@vitbhopal.ac.in'),
        ('Zara Khan', '2024', 'zara.k', 'pass123', 'zara.k@vitbhopal.ac.in'),
        ('Yash Patel', '2024', 'yash.p', 'pass123', 'yash.p@vitbhopal.ac.in'),
        ('Aisha Reddy', '2024', 'aisha.r', 'pass123', 'aisha.r@vitbhopal.ac.in'),
        ('Dev Kumar', '2024', 'dev.k', 'pass123', 'dev.k@vitbhopal.ac.in'),
        ('Tanya Sharma', '2024', 'tanya.s', 'pass123', 'tanya.s@vitbhopal.ac.in'),
        ('Nikhil Joshi', '2024', 'nikhil.j', 'pass123', 'nikhil.j@vitbhopal.ac.in')
    ]

    # Save login credentials to CSV
    with open('additional_login_credentials.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Type', 'Name', 'Username', 'Password', 'Email'])
        
        # Add teachers
        for name, dept, username, password, email in new_teachers:
            try:
                cursor.execute('''
                    INSERT INTO teachers (name, department, username, password, email) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (name, dept, username, generate_password_hash(password), email))
                writer.writerow(['Teacher', name, username, password, email])
                print(f"Added teacher: {name}")
            except Exception as e:
                print(f"Error adding teacher {name}: {str(e)}")

        # Add students
        for name, batch, username, password, email in new_students:
            try:
                cursor.execute('''
                    INSERT INTO students (name, batch, username, password, email) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (name, batch, username, generate_password_hash(password), email))
                writer.writerow(['Student', name, username, password, email])
                print(f"Added student: {name}")
            except Exception as e:
                print(f"Error adding student {name}: {str(e)}")

    # Create cabin status entries for new teachers
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_slots = ['8:30 AM', '10:05 AM', '11:40 AM', '1:15 PM', '2:50 PM', '4:25 PM', '6:00 PM']
    
    cursor.execute('SELECT id FROM teachers WHERE id NOT IN (SELECT DISTINCT teacher_id FROM cabin_status)')
    new_teacher_ids = [row[0] for row in cursor.fetchall()]

    for teacher_id in new_teacher_ids:
        for day in days:
            for time_slot in time_slots:
                try:
                    cursor.execute('''
                        INSERT INTO cabin_status (teacher_id, day, time_slot, status)
                        VALUES (%s, %s, %s, %s)
                    ''', (teacher_id, day, time_slot, 'Available'))
                except Exception as e:
                    print(f"Error adding cabin status for teacher {teacher_id}: {str(e)}")

    conn.commit()
    cursor.close()
    conn.close()

    print("\nAdditional users created successfully!")
    print("Login credentials saved to additional_login_credentials.csv")

if __name__ == "__main__":
    add_more_users() 