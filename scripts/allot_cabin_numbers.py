import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='sql12.freemysqlhosting.net',
        user='sql12752768',
        password='III99fbDnZ',
        database='sql12752768'
    )

def allot_cabin_numbers():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all teachers grouped by department
        cursor.execute('''
            SELECT id, name, department 
            FROM teachers 
            ORDER BY department, name
        ''')
        teachers = cursor.fetchall()

        # Dictionary to keep track of room numbers per department
        dept_counters = {}
        
        # Update cabin numbers
        for teacher_id, name, department in teachers:
            if department not in dept_counters:
                dept_counters[department] = 1
            
            # Create cabin number based on department and counter
            # Format: First letter of each word in department + room number
            dept_code = ''.join(word[0].upper() for word in department.split())
            cabin_number = f"{dept_code}-{dept_counters[department]:02d}"
            
            cursor.execute('''
                UPDATE teachers 
                SET cabin_number = %s 
                WHERE id = %s
            ''', (cabin_number, teacher_id))
            
            print(f"Allotted cabin {cabin_number} to {name} ({department})")
            dept_counters[department] += 1

        conn.commit()
        print("\nCabin numbers allotted successfully!")

    except Exception as e:
        print(f"Error allotting cabin numbers: {str(e)}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    allot_cabin_numbers() 