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
    
    # CLASSES TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Classes (
                    Class_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR,
                    Description VARCHAR,
                    Type VARCHAR
                    )
                 ''')
    
    # INTERNSHIP TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Internship (
                    Intern_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR,
                    Description VARCHAR,
                    Is_Gov BINARY
                    )
                 ''')
    
    # CERTIFICATION TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Certification (
                    Cert_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR,
                    Description VARCHAR,
                    Level VARCHAR
                    )
                 ''')
    
    # CLASS ENROLLMENT TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Class_Enrollment (
                    CE_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                    FOREIGN KEY(UIN) REFERENCES College_students(UIN),
                    FOREIGN KEY(Class_ID) REFERENCES Classes(Class_ID),
                    Status VARCHAR, 
                    Semester VARCHAR,
                    Year YEAR
                    )
                 ''')
    
    # CERTIFICATION ENROLLMENT TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Cert_Enrollment (
                    CertE_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                    FOREIGN KEY(UIN) REFERENCES College_students(UIN),
                    FOREIGN KEY(Cert_ID) REFERENCES Certification(Cert_ID),
                    FOREIGN KEY(Program_Num) REFERENCES Programs(Program_Num),
                    Status VARCHAR, 
                    Training_Status VARCHAR,
                    Semester VARCHAR,
                    Year YEAR
                    )
                 ''')
    
    # INTERNSHIP APPLICATION TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Intern_App (
                    IA_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                    FOREIGN KEY(UIN) REFERENCES College_students(UIN),
                    FOREIGN KEY(Intern_ID) REFERENCES Internship(Intern_ID),
                    Status VARCHAR, 
                    Year YEAR
                    )
                 ''')

    print("Table created successfully")
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn   
