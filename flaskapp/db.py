import sqlite3
from flask import flash
from generate import *

# Database Initialization
def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    
    # USERS TABLE - Fredy Padron
    conn.execute(''' CREATE TABLE IF NOT EXISTS Users (
                    UIN INTEGER PRIMARY KEY,
                    First_Name TEXT NOT NULL,
                    M_Initial TEXT,
                    Last_Name TEXT NOT NULL,
                    Username TEXT UNIQUE NOT NULL,
                    Password TEXT NOT NULL,
                    User_Type TEXT NOT NULL,
                    Email TEXT UNIQUE NOT NULL,
                    Discord_Name TEXT NOT NULL,
                    Archived INTEGER NOT NULL
                    )''')

   # COLLEGE STUDENTS TABLE - Freddy Padron
    conn.execute(''' CREATE TABLE IF NOT EXISTS College_Students (
                    UIN INTEGER PRIMARY KEY,
                    Gender TEXT NOT NULL,
                    Hispanic_Or_Latino INTEGER NOT NULL,
                    Race TEXT NOT NULL,
                    US_Citizen INTEGER NOT NULL,
                    First_Generation INTEGER NOT NULL,
                    Birthdate DATE NOT NULL,
                    GPA REAL,
                    Major TEXT,
                    Minor TEXT ,
                    Second_Minor TEXT,
                    Exp_Graduation INTEGER,
                    School TEXT NOT NULL,
                    Classification TEXT NOT NULL,
                    Phone INTEGER,
                    Student_Type TEXT NOT NULL,
                    FOREIGN KEY(UIN) REFERENCES Users(UIN)
                    )
                ''')
    
    # EVENT TABLE - Christian Jeardoe
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
    
    # EVENT_TRACKING TABLE - Christian Jeardoe
    conn.execute(''' CREATE TABLE IF NOT EXISTS Event_Tracking (
                ET_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                Event_ID INTEGER,
                UIN INTEGER,
                FOREIGN KEY(Event_ID) REFERENCES Event(Event_ID),
                FOREIGN KEY(UIN) REFERENCES Users(UIN)
                )
            ''')
    
    # DOCUMENTS TABLE - Christian Jeardoe
    conn.execute(''' CREATE TABLE IF NOT EXISTS Documents (
                Doc_Num INTEGER PRIMARY KEY AUTOINCREMENT,
                App_Num INTEGER,
                Link VARCHAR(256),
                Doc_Type VARCHAR(50),
                Name TEXT,
                FOREIGN KEY(App_Num) REFERENCES Applications(App_Num)
                )
            ''')

    # PROGRAMS TABLE - Kelvin Zheng
    conn.execute(''' CREATE TABLE IF NOT EXISTS Programs (
                    program_num INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    archived INTEGER
                    )''')
    
    # APPLICATION TABLE - Kelvin Zheng
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
    
    # TRACK TABLE - Kelvin Zheng
    # possible status = ['Rejected', 'Enrolled', 'Completed', 'Dropped'] 
    conn.execute('''CREATE TABLE IF NOT EXISTS Track (
                    tracking_num INTEGER PRIMARY KEY AUTOINCREMENT,
                    program INTEGER,
                    student_num INTEGER,
                    status VARCHAR, 
                    FOREIGN KEY(program) REFERENCES Programs(program_num),
                    FOREIGN KEY(student_num) REFERENCES College_students(UIN)             
                  )''')
    
    # CLASSES TABLE - Alex Kilgore
    conn.execute(''' CREATE TABLE IF NOT EXISTS Classes (
                    Class_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR,
                    Description VARCHAR,
                    Type VARCHAR
                    )
                 ''')
    
    # INTERNSHIP TABLE - Alex Kilgore
    conn.execute(''' CREATE TABLE IF NOT EXISTS Internship (
                    Intern_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR,
                    Description VARCHAR,
                    Is_Gov BINARY
                    )
                 ''')
    
    # CERTIFICATION TABLE - Alex Kilgore
    conn.execute(''' CREATE TABLE IF NOT EXISTS Certification (
                    Cert_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR,
                    Description VARCHAR,
                    Level VARCHAR
                    )
                 ''')
    
    # CLASS ENROLLMENT TABLE - Alex Kilgore
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

    # CERTIFICATION ENROLLMENT TABLE - Alex Kilgore
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
    
    # INTERNSHIP APPLICATION TABLE - Alex Kilgore
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
    
    # View of Left Join from Users and College Students table: Admins have NULL values for student attributes
    # - Freddy Padron
    conn.execute('''CREATE VIEW IF NOT EXISTS View_CollegeStudentDetails AS
        SELECT u.*, cs.Gender, cs.Hispanic_Or_Latino, cs.Race, cs.US_Citizen, cs.First_Generation, 
            cs.Birthdate, cs.GPA, cs.Major, cs.Minor, cs.Second_Minor, cs.Exp_Graduation, 
            cs.School, cs.Classification, cs.Phone, cs.Student_Type
        FROM Users u
        LEFT JOIN College_Students cs ON u.UIN = cs.UIN
    ''')

    # View of LEFT JOIN of Application and Track and JOIN of Application and program
    # Used to make querying for program application details easier
    # - Kelvin Zheng
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
                LEFT JOIN Track ON Application.UIN = Track.student_num AND Application.program_num = Track.program
                JOIN Programs ON Application.program_num = Programs.program_num
                ''')

    # View of students in programs that are not rejected
    # Makes querying for data about students that were at some point in a program easier
    # - Kelvin Zheng
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
    
    # View of documents, applications, and programs - Christian Jeardoe
    conn.execute('''CREATE VIEW IF NOT EXISTS View_DocumentsApplicationPrograms AS
                    SELECT
                        Programs.name AS ProgramName,
                        Application.app_num AS app_num,
                        Application.program_num AS program_num,
                        Application.UIN AS UIN,
                        Documents.Doc_Num AS Doc_Num,
                        Documents.Link AS Link,
                        Documents.Doc_Type AS Doc_Type,
                        Documents.Name AS Name
                    FROM Application
                    JOIN Documents ON Application.app_num = Documents.App_Num
                    JOIN Programs ON Application.program_num = Programs.program_num;
                    ''')

    # Join classes and enrollments - Alex Kilgore
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

    # Join Internships and Intern_App - Alex Kilgore
    conn.execute('''CREATE VIEW IF NOT EXISTS View_InternAppDetails AS
    SELECT * FROM Internship
    JOIN Intern_App ON Internship.Intern_ID = Intern_App.Intern_ID;
    ''')

    # Get user's unenrolled certifications -Alex Kilgore, Freddy Padron
    conn.execute('''CREATE VIEW IF NOT EXISTS Unenrolled_Certifications AS
        SELECT u.UIN, c.Cert_ID, c.Name, c.Description, c.Level, ce.Status, ce.Training_Status, ce.Semester, ce.Year
        FROM Users u
        JOIN Certification c
        LEFT JOIN Cert_Enrollment ce ON u.UIN = ce.UIN AND c.Cert_ID = ce.Cert_ID
        WHERE ce.CertE_Num IS NULL;
''')


    # Join Certifications and Cert_Enrollments - Alex Kilgore
    conn.execute('''CREATE VIEW IF NOT EXISTS View_CertEnrollmentDetails AS
        SELECT Cert_Enrollment.*, Certification.*
        FROM Cert_Enrollment
        LEFT JOIN Certification ON Cert_Enrollment.Cert_ID = Certification.Cert_ID;
        ''')    
    
    #  ---------- INDEXES ---------- 
    
    conn.execute('CREATE INDEX IF NOT EXISTS idx_event_uin ON Event(UIN)') # Christian Jeardoe
    conn.execute('CREATE INDEX IF NOT EXISTS idx_application_uin ON Application(UIN)') # Kelvin Zheng
    conn.execute("CREATE INDEX IF NOT EXISTS idx_track_program ON Track(program)") # Kelvin Zheng
    conn.execute("CREATE INDEX IF NOT EXISTS idx_class_enrollment_uin ON Class_Enrollment(UIN)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_intern_app_uin ON Intern_App(UIN)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cert_enrollment_uin ON Cert_Enrollment(UIN)")
    conn.execute('CREATE INDEX IF NOT EXISTS idx_application_num ON Documents(app_num)') # Christian Jeardoe
    conn.commit()
    
    

    print("Database initialized succesfully")
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn   
