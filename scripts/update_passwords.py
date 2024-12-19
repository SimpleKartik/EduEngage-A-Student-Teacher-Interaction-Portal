import mysql.connector
from werkzeug.security import generate_password_hash
import csv

def get_db_connection():
    return mysql.connector.connect(
        host='sql12.freemysqlhosting.net',
        user='sql12752768',
        password='III99fbDnZ',
        database='sql12752768'
    )

def update_student_passwords():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all students
        cursor.execute('SELECT id, name, username, email FROM students ORDER BY name')
        students = cursor.fetchall()

        # Save new credentials to CSV
        with open('updated_student_credentials.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Username', 'Email', 'New Password'])

            # Update passwords sequentially
            for index, (student_id, name, username, email) in enumerate(students, 1):
                # Create sequential password
                new_password = f"VITStudent{index:03d}"  # Will create VITStudent001, VITStudent002, etc.
                
                # Update password in database
                cursor.execute('''
                    UPDATE students 
                    SET password = %s 
                    WHERE id = %s
                ''', (generate_password_hash(new_password), student_id))
                
                # Save to CSV
                writer.writerow([name, username, email, new_password])
                print(f"Updated password for {name}: {new_password}")

        conn.commit()
        print("\nAll student passwords updated successfully!")
        print("New credentials saved to updated_student_credentials.csv")

    except Exception as e:
        print(f"Error updating passwords: {str(e)}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_student_passwords() 