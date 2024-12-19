from werkzeug.security import generate_password_hash
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='sql12.freemysqlhosting.net',
        user='sql12752768',
        password='III99fbDnZ',
        database='sql12752768'
    )

def create_teacher(username, password, name, department, email):
    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO teachers (username, password, name, department, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, hashed_password, name, department, email))
        
        conn.commit()
        return True, "Teacher created successfully"
    except mysql.connector.Error as err:
        return False, f"Error: {str(err)}"
    finally:
        cursor.close()
        conn.close()

def create_student(username, password, name, batch, email):
    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO students (username, password, name, batch, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, hashed_password, name, batch, email))
        
        conn.commit()
        return True, "Student created successfully"
    except mysql.connector.Error as err:
        return False, f"Error: {str(err)}"
    finally:
        cursor.close()
        conn.close() 