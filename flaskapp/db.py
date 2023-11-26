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
    
    # EVENT TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Event (
                Event_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                FOREIGN KEY(UIN) REFERENCES Users(UIN),
                FOREIGN KEY(Program_Num) REFERENCES Programs(Program_Num),
                Start_Date DATE,
                Time TIME,
                Location VARCHAR(50),
                End_Date DATE,
                Time TIME,
                Event_Type VARCHAR(50)
                )
            ''')
    
    # EVENT_TRACKING TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Event_Tracking (
                ET_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                FOREIGN KEY(Event_ID) REFERENCES Event(Event_ID),
                FOREIGN KEY(UIN) REFERENCES Users(UIN),
                )
            ''')
    
    # DOCUMENTS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Documents (
                Doc_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                FOREIGN KEY(App_Num) REFERENCES Applications(App_Num),
                Link VARCHAR(50),
                Doc_Type VARCHAR(50),
                )
            ''')

    print("Table created successfully")
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn   
