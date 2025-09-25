#!/usr/bin/env python3
"""
Simple database test script for EduEngage
This script tests the database connection and checks if tables exist
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection and check tables"""
    try:
        # Connect to database
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
        
        print("✅ Database connection successful!")
        
        cursor = connection.cursor()
        
        # Check if tables exist
        tables_to_check = ['teachers', 'students', 'cabin_status', 'project_groups', 'project_group_members', 'projects']
        
        print("\n📋 Checking tables:")
        for table in tables_to_check:
            try:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                result = cursor.fetchone()
                if result:
                    # Count records in table
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {table}: {count} records")
                else:
                    print(f"   ❌ {table}: Table not found")
            except Exception as e:
                print(f"   ❌ {table}: Error - {e}")
        
        # Test login credentials
        print("\n🔐 Testing login credentials:")
        
        # Check teachers
        cursor.execute("SELECT username, name FROM teachers LIMIT 3")
        teachers = cursor.fetchall()
        if teachers:
            print("   Teachers found:")
            for username, name in teachers:
                print(f"      - {name} (username: {username})")
        else:
            print("   ❌ No teachers found")
        
        # Check students
        cursor.execute("SELECT username, name FROM students LIMIT 3")
        students = cursor.fetchall()
        if students:
            print("   Students found:")
            for username, name in students:
                print(f"      - {name} (username: {username})")
        else:
            print("   ❌ No students found")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Database test completed successfully!")
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing EduEngage Database Connection...")
    print("=" * 50)
    
    success = test_database_connection()
    
    if success:
        print("\n✅ Your database is working! You can proceed with deployment.")
        print("\nNext steps:")
        print("1. Deploy to Render")
        print("2. Set environment variables in Render dashboard")
        print("3. Test the /health endpoint")
        print("4. Test login functionality")
    else:
        print("\n❌ Database connection failed. Please check your credentials.")
        print("\nTroubleshooting:")
        print("1. Verify database credentials")
        print("2. Check if FreeMySQLHosting service is active")
        print("3. Ensure your IP is not blocked")
