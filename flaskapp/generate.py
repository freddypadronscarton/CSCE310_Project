import sqlite3
import random
from datetime import datetime
from db import *
import os

# GENERATES MOCK DATA

def insert_mock_data():
    # remove old db
    os.remove("database.db")
    # re-initialize
    init_sqlite_db()
    # connect
    conn = sqlite3.connect('database.db')
    
    # call insertion functions
    insert_users(conn)
    insert_programs(conn)
    
    conn.commit()

def random_date(start_year, end_year):
    return datetime.strftime(datetime(random.randint(start_year, end_year), random.randint(1, 12), random.randint(1, 28)), '%Y-%m-%d')


def insert_programs(conn):
    program_names = [
        "Cyber Leader Development Program (CLDP)",
        "Virtual Institutes for Cyber and Electromagnetic Spectrum Research and Employ (VICEROY)",
        "Pathways",
        "CyberCorps: Scholarship for Service (SFS)",
        "DoD Cybersecurity Scholarship Program (CySP)"
    ]

    for i, name in enumerate(program_names, start=1):
        conn.execute('''INSERT INTO Programs (program_num, name, description, archived) VALUES (?, ?, ?, ?)''', 
                     (i, name, 'Sample Program', 0))

def insert_users(conn):
    # Insert Users
    first_names = ["John", "Jill", "Bill", "Ana", "Freddy", "Kelvin", "Alex", "Christian"]
    last_names = ["Smith", "Jones", "Padron", "Zheng", "Jeardoe", "Kilgore", "Lanclos", "Zachry"]
    user_types = ["k12_student", "college_student"]
    for i in range(1, 21):
        user_type = random.choice(user_types)
        conn.execute('''INSERT INTO Users (UIN, First_Name, M_Initial, Last_Name, Username, Password, User_Type, Email, Discord_Name, Archived) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                     (i, f'{random.choice(first_names)}', 'M', f'{random.choice(last_names)}', f'User{i}', 'password', f'{user_type}', f'user{i}@mockData.com', f'DiscordUser{i}', 0))

        if user_type == "college_student":
            conn.execute('''INSERT INTO College_Students (UIN, Gender, Hispanic_Or_Latino, Race, US_Citizen, First_Generation, Birthdate, GPA, Major, Minor, Second_Minor, Exp_Graduation, School, Classification, Phone, Student_Type) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (i, 'male' if i % 2 == 0 else 'female', random.randint(0, 1), 'other', random.randint(0, 1), random.randint(0, 1), random_date(1990, 2005), round(random.uniform(2.0, 4.0), 2), 'Computer Science', None, None, 2024, 'Texas A&M University', 'Other', 1234567890, 'college_student'))
        if user_type == "k12_student":
            conn.execute('''INSERT INTO College_Students (UIN, Gender, Hispanic_Or_Latino, Race, US_Citizen, First_Generation, Birthdate, School, Classification, Phone, Student_Type) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (i, 'male' if i % 2 == 0 else 'female', random.randint(0, 1), 'other', random.randint(0, 1), random.randint(0, 1), random_date(1990, 2005), 'Cinco Ranch High School', 'K', 1234567890, 'k12_student'))




    # # Insert Events
    # for i in range(1, 6):
    #     conn.execute('''INSERT INTO Event (Event_ID, Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type) 
    #                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
    #                  (i, random.randint(1, 5), random.randint(1, 10), random_date(2023, 2023), '12:00', 'Location', random_date(2023, 2023), 'Type'))

    # # Insert Event Tracking
    # for i in range(1, 6):
    #     conn.execute('''INSERT INTO Event_Tracking (ET_Num, Event_ID, UIN) VALUES (?, ?, ?)''', 
    #                  (i, i, random.randint(1, 10)))

    # # Insert Documents
    # for i in range(1, 6):
    #     conn.execute('''INSERT INTO Documents (Doc_Num, App_Num, Link, Doc_Type) VALUES (?, ?, ?, ?)''', 
    #                  (i, i, f'http://example.com/doc{i}.pdf', 'Type'))

    # # Insert Applications
    # for i in range(1, 6):
    #     conn.execute('''INSERT INTO Application (app_num, program_num, UIN, uncom_cert, com_cert, purpose_statement) VALUES (?, ?, ?, ?, ?, ?)''', 
    #                  (i, random.randint(1, 5), random.randint(1, 10), 'uncert', 'cert', 'Purpose'))

    # # Insert Certifications
    # for i in range(1, 6):
    #     conn.execute('''INSERT INTO Certification (Cert_ID, Name, Description, Level) VALUES (?, ?, ?, ?)''', 
    #                  (i, f'Certification{i}', f'Description{i}', 'Level1'))

    # # Insert Classes
    # for i in range(1, 6):
    #     conn.execute('''INSERT INTO Classes (Class_ID, Name, Description, Type) VALUES (?, ?, ?, ?)''', 
    #                  (i, f'Class{i}', f'Description{i}', 'Type'))

