# Placement Portal

## Overview

The Placement Portal is a Flask-based web application designed to support the campus recruitment process through role-based access for administrators, companies, and students. The system centralizes company registration, drive approval, student applications, and application status management within a single platform.

## Core Functionality

### Administrator

- Review and approve company registrations.
- Review and approve placement drives.
- View student, company, drive, and application records.
- Blacklist students or companies when required.
- Search student and company records from the administrative dashboard.

### Company

- Register and wait for administrative approval.
- Create and manage placement drives.
- View applications submitted for each drive.
- Update application status to shortlisted, selected, or rejected.
- Update company profile details.

### Student

- Register and maintain a student profile.
- Upload and update a PDF resume.
- View active placement drives.
- Apply for eligible drives.
- Track application status and application history.

## Technology Stack

- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite
- Werkzeug
- Jinja2 templates

## Project Structure

- `app.py` - Application entry point and Flask configuration.
- `routes.py` - Blueprint containing authentication, dashboard, and workflow routes.
- `models.py` - Database models and relationships.
- `create_database.py` - Database initialization script and default admin creation.
- `templates/` - HTML templates for all user roles.
- `statics/uploads/` - Resume upload directory.

## Setup

1. Create and activate a Python virtual environment.
2. Install the dependencies listed in `requirements.txt`.
3. Initialize the database by running `create_database.py`.
4. Start the application using `app.py`.

## Default Administrator Account

The database initialization script creates a default administrator account with the following credentials:

- Username: `admin`
- Password: `admin123`

## Notes

- Student resume uploads are restricted to PDF files.
- The application uses SQLite for local storage.
- Company accounts require administrative approval before login access is granted.

