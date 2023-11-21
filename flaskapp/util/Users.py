from flask import flash
from db import *


# CREATES
def create_user(conn, user_info):
    user_type = user_info['user_type']
    # INSERT into users table
    conn.execute('''INSERT INTO users (
        UIN,
        First_Name,
        M_Initial,
        Last_Name,
        Username,
        Password,
        User_Type,
        Email,
        Discord_Name,
        Archived) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_info['uin'],
            user_info['first_name'],
            user_info["middle_initial"],
            user_info["last_name"],
            user_info["username"], 
            user_info["password"],
            user_type,
            user_info["email"],
            user_info["discord"],
            1 if user_type == "admin" else 0 # Archive new admins by default
        ))
    
def create_college_student(conn, user_info):
    # add to college_students table
    conn.execute('''INSERT INTO College_Students (
        UIN,
        Gender,
        Hispanic_Or_Latino,
        Race, 
        US_Citizen,
        First_Generation,
        Birthdate,
        GPA,
        Major,
        Minor,
        Second_Minor,
        Exp_Graduation,
        School,
        Classification,
        Phone,
        Student_Type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_info["uin"],
        user_info["gender"],
        1 if "hispanic_or_latino" in user_info else 0,
        user_info["race"],
        1 if "first_gen" in user_info else 0,
        1 if "US_citizen" in user_info else 0,
        user_info["birth_date"],
        user_info["gpa"],
        user_info["major"],
        user_info["minor"] ,
        user_info["second_minor"],
        user_info["Exp_Graduation"],
        user_info["school"],
        user_info["classification"],
        "".join(user_info["phone_number"].split("-")),
        "college_student"))
    
def create_k12_student(conn, user_info):
    # add to college_students table
    conn.execute('''INSERT INTO College_Students (
        UIN,
        Gender,
        Hispanic_Or_Latino,
        Race, 
        US_Citizen,
        First_Generation,
        Birthdate,
        GPA,
        Major,
        Minor,
        Second_Minor,
        Exp_Graduation,
        School,
        Classification,
        Phone,
        Student_Type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
        user_info["uin"],
        user_info["k12_gender"],
        1 if "k12_hispanic_or_latino" in user_info else 0,
        user_info["k12_race"],
        1 if "k12_first_gen" in user_info else 0,
        1 if "k12_US_citizen" in user_info else 0,
        user_info["k12_birth_date"],
        None,
        None,
        None,
        None,
        None,
        user_info["k12_school"],
        user_info["k12_classification"],
        "".join(user_info["k12_phone_number"].split("-")),
        "k12_student"))

def register_user(conn, user_info):
    
    # Create entry in Users table
    create_user(conn, user_info)

    user_type = user_info['user_type']
        
    if user_type == "k12_student":
        create_k12_student(conn, user_info)
    
    if user_type == "college_student":
        create_college_student(conn, user_info)
    
    flash("Successfully registered new user!", "Success")
          
# UPDATES
def update_user_field(conn, UIN, field, value):
    query = f"UPDATE users SET {field} = ? WHERE UIN = ?"
    conn.execute(query, (value, UIN))
    
def delete_user(conn, UIN):
    conn.execute(f"DELETE FROM College_Students WHERE UIN = {UIN}")
    conn.execute(f"DELETE FROM Users WHERE UIN = {UIN}")
    
# DELETES

def delete_student(conn, UIN):
    conn.execute(f"DELETE FROM College_Students WHERE UIN = {UIN}")