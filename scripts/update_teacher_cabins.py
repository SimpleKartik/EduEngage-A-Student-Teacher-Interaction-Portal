import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="student_project_db"
    )

def update_cabin_numbers():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all teachers
        cursor.execute('SELECT id, name FROM teachers ORDER BY id')
        teachers = cursor.fetchall()

        # Update cabin numbers (format: AB-1xx where xx is sequential number)
        for index, (teacher_id, name) in enumerate(teachers, 1):
            cabin_number = f"AB-{index:03d}"
            cursor.execute('''
                UPDATE teachers 
                SET cabin_number = %s 
                WHERE id = %s
            ''', (cabin_number, teacher_id))
            print(f"Updated cabin number for {name}: {cabin_number}")

        conn.commit()
        print("\nAll cabin numbers updated successfully!")

    except Exception as e:
        print(f"Error updating cabin numbers: {str(e)}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_cabin_numbers() 