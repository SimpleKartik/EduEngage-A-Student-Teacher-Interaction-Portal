# EduEngage - Student Teacher Interaction Portal

A Flask-based web application for managing student-teacher interactions, project groups, and cabin status at VIT Bhopal University.

## Features

- **Student Login & Dashboard**
- **Teacher Login & Dashboard**
- **Project Group Management**
- **Cabin Status Tracking**
- **Faculty Search & Scheduling**

## Quick Start

### Prerequisites
- Python 3.7+
- MySQL Database

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables (see `.env.example`)

4. Run the application:
   ```bash
   python app.py
   ```

### Database Setup

Run the database setup script:
```bash
python scripts/setup_database.py
python scripts/create_initial_data.py
```

### Test Credentials

**Teachers:**
- Username: `john.smith`, Password: `pass123`
- Username: `sarah.j`, Password: `pass123`

**Students:**
- Username: `alice.c`, Password: `pass123`
- Username: `bob.w`, Password: `pass123`

## Deployment

### Render Deployment

1. Connect your GitHub repository to Render
2. Set the following environment variables:
   - `DB_HOST`: Your database host
   - `DB_USER`: Your database username
   - `DB_PASSWORD`: Your database password
   - `DB_NAME`: Your database name
   - `SECRET_KEY`: A secure secret key
   - `FLASK_ENV`: production

3. Deploy and test the `/health` endpoint

## Project Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile             # Render deployment configuration
├── static/              # CSS, JS, and images
├── templates/           # HTML templates
├── scripts/             # Database setup scripts
└── utils/               # Utility functions
```

## Health Check

Visit `/health` to check if the application and database are working correctly.

## License

This project is for educational purposes.
