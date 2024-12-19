import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.user_management import create_teacher, create_student

def create_initial_teachers():
    teachers = [
        {
            'username': 'teacher1',
            'password': 'secure_password1',
            'name': 'John Doe',
            'department': 'Computer Science',
            'email': 'john.doe@vit.ac.in'
        },
        # Add more teachers as needed
    ]
    
    for teacher in teachers:
        success, message = create_teacher(**teacher)
        print(f"Creating teacher {teacher['username']}: {message}")

def create_initial_students():
    students = [
        {
            'username': 'student2',
            'password': 'mkc123',
            'name': 'Jane Smith',
            'batch': '2023',
            'email': 'jane1.smith@vit.ac.in'
        },
        # Add more students as needed
    ]
    
    for student in students:
        success, message = create_student(**student)
        print(f"Creating student {student['username']}: {message}")

# You can add this to your create_initial_users.py script
test_student = {
    'username': 'test_student',
    'password': 'test123',
    'name': 'Test Student',
    'batch': '2023',
    'email': 'test.student@vit.ac.in'
}

success, message = create_student(**test_student)
print(f"Creating test student: {message}")

if __name__ == "__main__":
    print("Creating initial users...")
    create_initial_teachers()
    create_initial_students()
    print("Done!") 