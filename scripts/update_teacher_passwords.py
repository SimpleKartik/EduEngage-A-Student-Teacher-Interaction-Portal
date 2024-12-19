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

def update_teacher_passwords():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all teachers
        cursor.execute('SELECT id, name, username, email, department FROM teachers ORDER BY name')
        teachers = cursor.fetchall()

        # Save new credentials to CSV
        with open('updated_teacher_credentials.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Department', 'Username', 'Email', 'New Password'])

            # Update passwords sequentially
            for index, (teacher_id, name, username, email, department) in enumerate(teachers, 1):
                # Create sequential password
                new_password = f"VITFaculty{index:02d}"  # Will create VITFaculty01, VITFaculty02, etc.
                
                # Update password in database
                cursor.execute('''
                    UPDATE teachers 
                    SET password = %s 
                    WHERE id = %s
                ''', (generate_password_hash(new_password), teacher_id))
                
                # Save to CSV
                writer.writerow([name, department, username, email, new_password])
                print(f"Updated password for {name} ({department}): {new_password}")

        conn.commit()
        print("\nAll teacher passwords updated successfully!")
        print("New credentials saved to updated_teacher_credentials.csv")

    except Exception as e:
        print(f"Error updating passwords: {str(e)}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_teacher_passwords() 