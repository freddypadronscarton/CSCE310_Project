import sqlite3

from flask import flash

# Database Initialization
def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    
    # ITEMS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    description TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )''')
    # USERS TABLE: is_admin = 'True/False'
    conn.execute(''' CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    email TEXT,
                    f_name TEXT,
                    l_name TEXT,
                    middle_initial TEXT,
                    phone_number TEXT,
                    gender TEXT,
                    birth_date DATE,
                    hispanic_or_latino TEXT,
                    race TEXT,
                    school TEXT,
                    student_type TEXT,
                    is_admin TEXT)''')
    # STUDENTS TABLE: in_college = 'True/False'
    conn.execute(''' CREATE TABLE IF NOT EXISTS students (
                    user_id INTEGER PRIMARY KEY,
                    in_college TEXT,
                    US_citizen TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )''')
    # ADMINS TABLE:
    conn.execute(''' CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    title TEXT,
                    authenticated INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )''')
    # COLLEGE STUDENTS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS college_students (
                    user_id INTEGER PRIMARY KEY,
                    UIN INTEGER,
                    first_gen TEXT,
                    classification TEXT,
                    major TEXT,
                    second_major TEXT,
                    minor TEXT,
                    second_minor TEXT,
                    gpa NUMBER,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )
                ''')
    # K12 STUDENTS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS k12_students (
                    user_id INTEGER PRIMARY KEY,
                    grade INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )''')

    print("Table created successfully")
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn   

# Register a new User
def register_user(conn, request, user_type):
    # INSERT into users table
    cursor = conn.execute('''INSERT INTO users (
        username,
        password,
        email,
        f_name,
        l_name,
        middle_initial,
        phone_number,
        gender,
        birth_date,
        hispanic_or_latino,
        race,
        school,
        student_type,
        is_admin,
        archived) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (request.form['username'],
            request.form['password'],
            request.form["email"],
            request.form["f_name"],
            request.form["l_name"], 
            request.form["middle_initial"],
            request.form["phone_number"],
            request.form["gender"],
            request.form["birth_date"],
            "True" if "hispanic_or_latino" in request.form else "False",
            request.form["race"],
            request.form["school"],
            user_type if not user_type == "admin" else None, # student_type
            "True" if user_type == "admin" else "False",
            1 if user_type == "admin" else 0) # is_admin
        )

    new_user_id = cursor.lastrowid  # Get the last inserted id

    # INSERT into subtype tables (admins, students, k12_students, college_students)
    if user_type == 'admin':
        conn.execute('INSERT INTO admins (user_id, title, authenticated) VALUES (?, ?, ?)',
                        (new_user_id, request.form["title"], 1))
        
    elif user_type == 'college_student':
        # add to students table
        conn.execute('INSERT INTO students (user_id, in_college, US_citizen) VALUES (?, ?, ?)',
                        (new_user_id, "True" if user_type == "college_student" else "False", "True" if "US_citizen" in request.form else "False"))
        
        # add to college_students table
        conn.execute('INSERT INTO college_students (user_id, UIN, first_gen, classification, major, second_major, minor, second_minor, gpa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (new_user_id, request.form["uin"], "True" if "first_gen" in request.form else "False", request.form["classification"], request.form["major"], request.form["second_major"], request.form["minor"], request.form["second_minor"], request.form["gpa"]))
    
    elif user_type == 'k12_student':
            # add to students table
        conn.execute('INSERT INTO students (user_id, in_college, US_citizen) VALUES (?, ?, ?)',
                        (new_user_id, "True" if user_type == "college_student" else "False", "True" if "US_citizen" in request.form else "False"))
        # add to k12_students table
        conn.execute('INSERT INTO k12_students (user_id, grade) VALUES (?, ?)',
                        (new_user_id, request.form["grade"]))

    
    conn.commit()
    flash("Successfully registered new user!", "Success")
    
        

def update_user_field(conn, user_id, field, value):
    query = f"UPDATE users SET {field} = ? WHERE user_id = ?"
    conn.execute(query, (value, user_id))
