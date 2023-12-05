import sqlite3
from flask import flash

# Database Initialization
def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    
    # conn.execute('''DROP TABLE Cert_Enrollment''')

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
                    First_Name TEXT NOT NULL,
                    M_Initial TEXT,
                    Last_Name TEXT NOT NULL,
                    Username TEXT UNIQUE NOT NULL,
                    Password TEXT NOT NULL,
                    User_Type TEXT NOT NULL,
                    Email TEXT UNIQUE NOT NULL,
                    Discord_Name TEXT UNIQUE NOT NULL,
                    Archived INTEGER NOT NULL
                    )''')

   # COLLEGE STUDENTS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS College_Students (
                    UIN INTEGER PRIMARY KEY,
                    Gender TEXT NOT NULL,
                    Hispanic_Or_Latino INTEGER NOT NULL,
                    Race TEXT NOT NULL,
                    US_Citizen INTEGER NOT NULL,
                    First_Generation INTEGER NOT NULL,
                    Birthdate DATE NOT NULL,
                    GPA REAL NOT NULL,
                    Major TEXT NOT NULL,
                    Minor TEXT ,
                    Second_Minor TEXT,
                    Exp_Graduation INTEGER NOT NULL,
                    School TEXT NOT NULL,
                    Classification TEXT NOT NULL,
                    Phone INTEGER NOT NULL,
                    Student_Type TEXT NOT NULL,
                    FOREIGN KEY(UIN) REFERENCES Users(UIN)
                    )
                ''')
    
    # EVENT TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Event (
                Event_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Program_Num INTEGER,
                UIN INTEGER,
                Start_Date DATE,
                Time TIME,
                Location VARCHAR(50),
                End_Date DATE,
                Event_Type VARCHAR(50),
                FOREIGN KEY(UIN) REFERENCES Users(UIN),
                FOREIGN KEY(Program_Num) REFERENCES Programs(Program_Num)
                )
            ''')
    
    # EVENT_TRACKING TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Event_Tracking (
                ET_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                Event_ID INTEGER,
                UIN INTEGER,
                FOREIGN KEY(Event_ID) REFERENCES Event(Event_ID),
                FOREIGN KEY(UIN) REFERENCES Users(UIN)
                )
            ''')
    
    # DOCUMENTS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Documents (
                Doc_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                App_Num INTEGER,
                Link VARCHAR(256),
                Doc_Type VARCHAR(50),
                FOREIGN KEY(App_Num) REFERENCES Applications(App_Num)
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
    
    # TRACK TABLE: status = ['Applied', 'Rejected', 'Enrolled', 'Completed', 'Inactive'] 
    conn.execute('''CREATE TABLE IF NOT EXISTS Track (
                    tracking_num INTEGER PRIMARY KEY AUTOINCREMENT,
                    program INTEGER,
                    student_num INTEGER,
                    status VARCHAR, 
                    FOREIGN KEY(program) REFERENCES Programs(program_num),
                    FOREIGN KEY(student_num) REFERENCES College_students(UIN)             
                  )''')
    
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
                    UIN INTEGER,
                    Class_ID INTEGER,
                    Status VARCHAR, 
                    Semester VARCHAR,
                    Year YEAR,
                    FOREIGN KEY(UIN) REFERENCES College_students(UIN),
                    FOREIGN KEY(Class_ID) REFERENCES Classes(Class_ID)
                    )
                 ''')

    # CERTIFICATION ENROLLMENT TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Cert_Enrollment (
                    CertE_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                    UIN INTEGER,
                    Cert_ID INTEGER,
                    Program_Num INTEGER,
                    Status VARCHAR, 
                    Training_Status VARCHAR,
                    Semester VARCHAR,
                    Year YEAR,
                    FOREIGN KEY(UIN) REFERENCES College_students(UIN),
                    FOREIGN KEY(Cert_ID) REFERENCES Certification(Cert_ID),
                    FOREIGN KEY(Program_Num) REFERENCES Programs(program_Num)
                    )
                 ''')
    
    # INTERNSHIP APPLICATION TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS Intern_App (
                    IA_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                    UIN INTEGER,
                    Intern_ID INTEGER,
                    Status VARCHAR, 
                    Year YEAR,
                    FOREIGN KEY(UIN) REFERENCES College_students(UIN),
                    FOREIGN KEY(Intern_ID) REFERENCES Internship(Intern_ID)
                    )
                 ''')
    
    
    #  ---------- VIEWS ----------
    
    # View of Left Join from Users and College Students table: Admins have NULL values for student attribut3es
    conn.execute('''CREATE VIEW IF NOT EXISTS View_CollegeStudentDetails AS
        SELECT u.*, cs.Gender, cs.Hispanic_Or_Latino, cs.Race, cs.US_Citizen, cs.First_Generation, 
            cs.Birthdate, cs.GPA, cs.Major, cs.Minor, cs.Second_Minor, cs.Exp_Graduation, 
            cs.School, cs.Classification, cs.Phone, cs.Student_Type
        FROM Users u
        LEFT JOIN College_Students cs ON u.UIN = cs.UIN
    ''')
    
    # Added track to the join so we can access the tracking status
    conn.execute('''CREATE VIEW IF NOT EXISTS View_ApplicationDetails AS
                SELECT 
                    Application.UIN, 
                    Application.app_num, 
                    Application.program_num, 
                    Programs.name, 
                    Programs.description,
                    Programs.archived, 
                    Application.uncom_cert, 
                    Application.com_cert, 
                    Application.purpose_statement, 
                    Track.status
                FROM 
                    Application
                LEFT JOIN Track ON Application.program_num = Track.program
                JOIN Programs ON Application.program_num = Programs.program_num
                ''')

    # INSERT STATEMENTS FOR THE SAKE OF TESTING GIVEN THAT ALEX'S CODE ISN"T DONE
    # Add Student
    # conn.execute('''INSERT INTO Track (program, student_num, status) 
    #              values (1, 3424, "Accepted")''')
    # Add Class
    # conn.execute('''INSERT INTO Classes (name, description, type) 
    #              values ("data science", "beginner data science class", "data science")''')
    # Add Class Enrollment
    # conn.execute('''INSERT INTO Class_enrollment (UIN, Class_ID, status) 
    #              values (3424, 6, "Enrolled")''')
    # Add Certification
    # conn.execute('''INSERT INTO Certification (Name, Description, Level)
    #              values ("cert1", "basic cyber certification", "1")''')
    # Add Certificatino Enrollment
    # conn.execute('''INSERT INTO Cert_enrollment (UIN, Cert_ID, Program_Num, Status, Training_status)
    #              values (3424, 1, 1, "Incomplete", "Enrolled")''')
    
    # Set Student program status to complete
    # conn.execute('''UPDATE TRACK SET STATUS = "Completed" WHERE student_num = 3424''')

    # conn.execute('''UPDATE Cert_enrollment
    #              SET Status = "Complete"
    #              WHERE CertE_Num = 2''')
    
    # Add Internship
    # conn.execute('''INSERT INTO Internship (Name, Description, Is_Gov)
    #              VALUES ("Gov Internship", "a govt internship", 1)''')
    # Add Internship Application
    # conn.execute('''INSERT INTO Intern_app (UIN, Intern_ID, Status, Year)
    #              VALUES (3424, 1, "Accepted", 2021)''')

    # conn.execute("DELETE FROM Classes WHERE Class_ID = 2")
    # conn.execute("DELETE FROM Track WHERE tracking_num = 2")
    # conn.execute("DELETE FROM Internship WHERE Intern_ID = 2")
    # conn.execute("DELETE FROM Intern_App WHERE IA_Num = 2")

    # View of students in programs that are not rejected
    conn.execute('''CREATE VIEW IF NOT EXISTS Program_Accepts AS
                 SELECT Tracking_num, Program, Student_num, Status FROM Track WHERE Status != "Rejected"
                 ''')
    
    # View of certifications students in programs are enrolled in, helps reduce number of JOINs in code
    conn.execute('''CREATE VIEW IF NOT EXISTS Program_student_certification_data AS
              SELECT
                 Program_Accepts.program,
                 Program_Accepts.student_num,
                 Cert_Enrollment.status,
                 Cert_Enrollment.training_status
              FROM
                 Program_Accepts
                 JOIN Cert_Enrollment
                 On Program_Accepts.student_num = Cert_Enrollment.UIN
                 JOIN Internship
                 ''')

    # Join classes and enrollments
    conn.execute('''CREATE VIEW IF NOT EXISTS View_ClassEnrollmentDetails AS
    SELECT
        CE.CE_Num,
        CE.UIN,
        CE.Class_ID,
        CE.Status,
        CE.Semester,
        CE.Year,
        C.Name AS Name,
        C.Description AS Description,
        C.Type AS Type
    FROM
        Class_Enrollment CE
        JOIN Classes C ON CE.Class_ID = C.Class_ID;
        ''')


    # conn.execute('''CREATE VIEW IF NOT EXISTS Student_Data AS 
    #              SELECT UIN, gender, hispanic_or_latino, race, us_citizen, 
    #              first_generation, GPA, major, student_type
    #              FROM College_students''')
    
    
    #  ---------- INDEXES ---------- 
    
    conn.execute('CREATE INDEX IF NOT EXISTS idx_event_uin ON Event(UIN)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_application_uin ON Application(UIN)')
    conn.execute("CREATE INDEX IF NOT EXISTS Track_Index ON Track(program)")

    
    conn.commit()

    print("Database initialized succesfully")
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn   
