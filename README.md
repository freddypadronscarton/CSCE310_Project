# Project Overview

This document outlines the functionalities and responsibilities of team members in the development of our web application. (Readme by Freddy Padron)

## How to Run the Application

Follow these steps to set up and run the application:

1. **Navigate to the Project Directory**
  ```
  cd CSCE310_Project/flaskapp
  ```


2. **Install Dependencies**
- Install Flask:
  ```
  pip install Flask
  ```
- Install Flask-Login for user authentication:
  ```
  pip install Flask-Login
  ```

3. **Start the Application**
  ```
  python app.py
  ```

## Admin Functionalities

### User Authentication & Roles - Freddy
- **Insert**
  - `templates/auth/register.html`
  - `routes/app.py` (triggers/endpoints)
  - `util/Users.py` (SQL Queries)
- **Update**
  - `templates/admin/admin_home.html`
  - `templates/admin/edit_user.html`
  - `templates/admin/changeUserTypeForm.html`
  - `routes/admin.py` (triggers/endpoints)
  - `util/Users.py` (SQL Queries)
- **Select**
  - `templates/admin/admin_home.html`
  - `routes/admin.py` (triggers/endpoints)
  - `util/Users.py` (SQL Queries)
- **Delete**
  - `templates/admin/admin_home.html`
  - `routes/admin.py` (triggers/endpoints)
  - `util/Users.py` (SQL Queries)

### Program Information Management - Kelvin
- **Insert**
  - `admin_add_program.html`
  - `admin.py`
  - `Programs.py`
- **Update**
  - `admin_update_program.html`
  - `admin.py`
  - `Programs.py`
- **Select**
  - `admin_view_programs.html`
  - `get_program_report.html`
  - `admin.py`
  - `Programs.py`
- **Delete**
  - `admin_view_programs.html`
  - `admin.py`
  - `Programs.py`

### Program Progress Tracking - Alex
- **Insert**
  - `progress.py`, `classes.py`, `internship.py`, `cert.py`
  - `add_classes.html`
  - `admin_add_internship.html`
  - `view_certs.html` (with flag = “add”)
- **Update**
  - `progress.py`, `classes.py`, `internship.py`, `cert.py`
  - `update_class.html`, `update_class_basic.html`
  - `update_intern.html`, `update_intern_basic.html`
  - `update_cert_enrollment.html`
- **Select**
  - `progress.py`, `classes.py`, `internship.py`, `cert.py`
  - `admin_program_progress.html`
  - `view_all_classes.html`
  - `view_all_internships.html`
  - `view_certs.html` (flag = “view”)
- **Delete**
  - `Progress.py`, `classes.py`, `internship.py`, `cert.py`
  - `admin_program_progress.html`
  - `view_all_classes.html`
  - `view_all_internships.html`
  - `view_certs.html` (flag = “view”)

### Event Management - Christian
- **Insert**
  - `Events.py`
  - `admin.py`
  - `admin_add_event.html`
  - `admin_attendee_control.html`
- **Update**
  - `Events.py`
  - `admin.py`
  - `update_event.html`
- **Select**
  - `Events.py`
  - `admin.py`
  - `admin_view_events.html`
  - `admin_attendee_control.html`
- **Delete**
  - `Events.py`
  - `admin.py`
  - `admin_view_events.html`
  - `admin_attendee_control.html`

## Student Functionalities

### User Authentication & Roles - Freddy
- **Insert**
  - `templates/auth/register.html`
  - `routes/app.py` (triggers/endpoints)
  - `util/Users.py` (SQL Queries)
- **Update**
  - `templates/auth/profile.html`
  - `templates/auth/passwordRecovery.html`
  - `routes/app.py` (triggers/endpoints)
  - `util/Users.py` (SQL Queries)
- **Select**
  - `templates/auth/profile.html`
  - `routes/app.py` (triggers/endpoints)
  - `util/Users.py` (SQL Queries)
- **Delete**
  - `templates/auth/profile.html`
  - `routes/app.py` (triggers/endpoints)
  - `util/Users.py` (SQL Queries)

### Program Information Management - Kelvin
- **Insert**
  - `program_application.html`
  - `application.py`
  - `programs.py`
  - `program_application.css`
- **Update**
  - `update_program_app.html`
  - `application.py`
  - `Programs.py`
  - `program_application.css`
- **Select**
  - `application_review.html`
  - `application.py`
  - `Programs.py`
- **Delete**
  - `application.py`
  - `Programs.py`

### Program Progress Tracking - Alex
- **Insert**
  - `app.py`, `classes.py`, `intern.py`, `cert.py`
  - `college_home.html`
  - `add_classes.html`
  - `add_internship_student.html`
  - `view_certs.html` (with flag = “add”)
- **Update**
  - `app.py`, `classes.py`, `intern.py`, `cert.py`
  - `update_class_student.html`
  - `update_internship_student.html`
  - `update_cert_enrollment.html`
- **Select**
  - `classes.py`, `intern.py`, `cert.py`
  - `view_classes.html`
  - `view_internships.html`
  - `view_certs.html` (flag = “view”)
- **Delete**
  - `classes.py`, `intern.py`, `cert.py`
  - `view_classes.html`
  - `view_internships.html`
  - `view_certs.html` (flag = “view”)

### Document Upload and Management - Christian
- **Insert**
  - `Documents.py`
  - `document.py`
  - `upload_document.html`
  - `college_home.html`
- **Update**
  - `Documents.py`
  - `document.py`
  - `update_document.html`
  - `document_display.html`
- **Select**
  - `Documents.py`
  - `document.py`
  - `document_display.html`
- **Delete**
  - `Documents.py`
  - `document.py`
  - `document_display.html`
