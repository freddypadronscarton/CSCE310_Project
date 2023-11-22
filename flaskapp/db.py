import sqlite3
from flask import flash

# Database Initialization
def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    
    # ITEMS TABLE (EXAMPLE)
    conn.execute(''' CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    UIN INTEGER,
                    name TEXT,
                    description TEXT,
                    FOREIGN KEY(UIN) REFERENCES Users(UIN)
                    )''')
    # USERS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Users (
                    UIN INTEGER PRIMARY KEY,
                    First_Name TEXT,
                    M_Initial TEXT,
                    Last_Name TEXT,
                    Username TEXT,
                    Password TEXT,
                    User_Type TEXT,
                    Email TEXT,
                    Discord_Name TEXT,
                    Archived INTEGER
                    )''')

   # COLLEGE STUDENTS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS College_Students (
                    UIN INTEGER PRIMARY KEY,
                    Gender TEXT,
                    Hispanic_Or_Latino INTEGER,
                    Race TEXT,
                    US_Citizen INTEGER,
                    First_Generation INTEGER,
                    Birthdate DATE,
                    GPA REAL,
                    Major TEXT,
                    Minor TEXT,
                    Second_Minor TEXT,
                    Exp_Graduation INTEGER,
                    School TEXT,
                    Classification TEXT,
                    Phone INTEGER,
                    Student_Type TEXT,
                    FOREIGN KEY(UIN) REFERENCES Users(UIN)
                    )
                ''')

    # PROGRAMS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Programs (
                    program_num INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    archived INTEGER
                    )''')
    
    # APPLICATION TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Application (
                    app_num INTEGER PRIMARY KEY AUTOINCREMENT,
                    program_num INTEGER,
                    UIN INTEGER,
                    uncom_cert TEXT,
                    com_cert TEXT,
                    purpose_statement TEXT,
                    FOREIGN KEY(program_num) REFERENCES Programs(program_num),
                    FOREIGN KEY(UIN) REFERENCES College_students(UIN)
                    )''')

    print("Table created successfully")
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn   
