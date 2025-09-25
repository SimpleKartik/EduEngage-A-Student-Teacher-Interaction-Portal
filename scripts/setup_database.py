import mysql.connector
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'sql12.freemysqlhosting.net'),
            user=os.getenv('DB_USER', 'sql12752768'),
            password=os.getenv('DB_PASSWORD', 'III99fbDnZ'),
            database=os.getenv('DB_NAME', 'sql12752768'),
            autocommit=True,
            connect_timeout=10,
            use_unicode=True,
            charset='utf8mb4'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise

def create_tables():
    """Create all necessary tables for the application"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create teachers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(100) NOT NULL,
                department VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                cabin_number VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Teachers table created/verified")
        
        # Create students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(100) NOT NULL,
                batch VARCHAR(10) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Students table created/verified")
        
        # Create cabin_status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cabin_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_id INT NOT NULL,
                day VARCHAR(10) NOT NULL,
                time_slot VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'Available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                UNIQUE KEY unique_slot (teacher_id, day, time_slot)
            )
        """)
        print("✓ Cabin status table created/verified")
        
        # Create project_groups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_groups (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_type VARCHAR(50) NOT NULL,
                team_leader_id INT NOT NULL,
                teacher_id INT,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_leader_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
            )
        """)
        print("✓ Project groups table created/verified")
        
        # Create project_group_members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_group_members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id INT NOT NULL,
                student_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES project_groups(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE KEY unique_member (group_id, student_id)
            )
        """)
        print("✓ Project group members table created/verified")
        
        # Create projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                guide VARCHAR(100),
                description TEXT,
                deadline DATE,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Projects table created/verified")
        
        print("\n🎉 All tables created successfully!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating tables: {err}")
        raise
    finally:
        cursor.close()
        conn.close()

def test_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_existing_data():
    """Check if there's existing data in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check teachers
        cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cursor.fetchone()[0]
        
        # Check students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        print(f"\n📊 Current data in database:")
        print(f"   Teachers: {teacher_count}")
        print(f"   Students: {student_count}")
        
        return teacher_count > 0 or student_count > 0
        
    except mysql.connector.Error as err:
        print(f"❌ Error checking data: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔧 Setting up EduEngage Database...")
    print("=" * 50)
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot proceed without database connection")
        exit(1)
    
    # Create tables
    create_tables()
    
    # Check existing data
    has_data = check_existing_data()
    
    if has_data:
        print("\n✅ Database already has data. You can proceed with testing.")
    else:
        print("\n⚠️  Database is empty. Run 'python scripts/create_initial_data.py' to add sample data.")
    
    print("\n🎯 Next steps:")
    print("1. Run: python scripts/create_initial_data.py")
    print("2. Test login with credentials from login_credentials.csv")
    print("3. Deploy to Render with environment variables set")
