# Database Setup Guide

## Current Situation
- ✅ Your database is **remote** (FreeMySQLHosting) - it's safe!
- ✅ Database credentials are already configured in your app
- ❌ You may need to verify tables exist and add sample data

## Database Information
- **Host:** sql12.freemysqlhosting.net
- **Database:** sql12752768
- **User:** sql12752768
- **Password:** III99fbDnZ

## Option 1: Quick Test (Recommended)

### Step 1: Deploy to Render
1. Push your code to GitHub
2. Deploy to Render with these environment variables:
   ```
   DB_HOST=sql12.freemysqlhosting.net
   DB_USER=sql12752768
   DB_PASSWORD=III99fbDnZ
   DB_NAME=sql12752768
   SECRET_KEY=your_secure_secret_key_here
   FLASK_ENV=production
   ```

### Step 2: Test Health Endpoint
Visit: `https://your-app.onrender.com/health`

If it shows `{"status": "healthy", "database": "connected"}`, your database is working!

### Step 3: Test Login
Use these test credentials:
- **Teacher:** username: `john.smith`, password: `pass123`
- **Student:** username: `alice.c`, password: `pass123`

## Option 2: Manual Database Setup

If you want to set up the database manually, here are the SQL commands:

### Create Tables
```sql
-- Teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    cabin_number VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    batch VARCHAR(10) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cabin status table
CREATE TABLE IF NOT EXISTS cabin_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    day VARCHAR(10) NOT NULL,
    time_slot VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    UNIQUE KEY unique_slot (teacher_id, day, time_slot)
);

-- Project groups table
CREATE TABLE IF NOT EXISTS project_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_type VARCHAR(50) NOT NULL,
    team_leader_id INT NOT NULL,
    teacher_id INT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_leader_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Project group members table
CREATE TABLE IF NOT EXISTS project_group_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    student_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES project_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_member (group_id, student_id)
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    guide VARCHAR(100),
    description TEXT,
    deadline DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Add Sample Data
```sql
-- Insert sample teachers (passwords are hashed)
INSERT INTO teachers (name, department, username, password, email) VALUES
('Dr. John Smith', 'Computer Science', 'john.smith', '$pbkdf2:sha256:260000$...', 'john.smith@vitbhopal.ac.in'),
('Dr. Sarah Johnson', 'Electronics', 'sarah.j', '$pbkdf2:sha256:260000$...', 'sarah.j@vitbhopal.ac.in'),
('Prof. Michael Brown', 'Mechanical', 'michael.b', '$pbkdf2:sha256:260000$...', 'michael.b@vitbhopal.ac.in');

-- Insert sample students
INSERT INTO students (name, batch, username, password, email) VALUES
('Alice Cooper', '2024', 'alice.c', '$pbkdf2:sha256:260000$...', 'alice.c@vitbhopal.ac.in'),
('Bob Wilson', '2024', 'bob.w', '$pbkdf2:sha256:260000$...', 'bob.w@vitbhopal.ac.in'),
('Charlie Brown', '2024', 'charlie.b', '$pbkdf2:sha256:260000$...', 'charlie.b@vitbhopal.ac.in');
```

## Option 3: Install Python and Run Setup Scripts

### Install Python
1. Download Python from https://python.org
2. Install with "Add to PATH" option checked
3. Restart your terminal

### Run Setup Scripts
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database tables
python scripts/setup_database.py

# Add sample data
python scripts/create_initial_data.py
```

## Test Credentials

After setup, you can use these credentials to test:

### Teachers
- Username: `john.smith`, Password: `pass123`
- Username: `sarah.j`, Password: `pass123`
- Username: `michael.b`, Password: `pass123`

### Students
- Username: `alice.c`, Password: `pass123`
- Username: `bob.w`, Password: `pass123`
- Username: `charlie.b`, Password: `pass123`

## Next Steps

1. **Deploy to Render** (easiest option)
2. **Set environment variables** in Render dashboard
3. **Test the health endpoint** to verify database connection
4. **Test login functionality** with sample credentials

Your database is safe and should work once properly deployed!
