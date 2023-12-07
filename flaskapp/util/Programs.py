from flask import flash
from db import *

def get_program(conn, program_num):
  return conn.execute('SELECT * FROM Programs WHERE program_num=?', (program_num, )).fetchone()

# These functions are mainly meant for admin pages
def is_program_name_taken(conn, program_name):
  program_exist = conn.execute('SELECT COUNT(*) FROM Programs WHERE name=?', (program_name, )).fetchone()[0]
  if (program_exist > 0):
    return True
  else:
    return False
  
def add_new_program(conn, program_name, program_descr):
  conn.execute('INSERT INTO Programs (name, description, archived) VALUES (?, ?, 0)', (program_name, program_descr))
  conn.commit()

def get_all_programs(conn):
  return conn.execute('SELECT * FROM Programs').fetchall()

def get_all_unarchived_programs(conn):
  return conn.execute('SELECT * FROM Programs WHERE archived = 0').fetchall()

def update_program_info(conn, program_num, program_name, program_descr):
  conn.execute('UPDATE Programs SET name=?, description=? WHERE program_num=?', (program_name, program_descr, program_num))
  conn.commit()

def update_program_archive_status(conn, program_num, archived):
  conn.execute('UPDATE Programs SET archived=? WHERE program_num=?', (archived, program_num))
  conn.commit()

def delete_program_backend(conn, program_num):
  conn.execute('DELETE FROM Programs WHERE program_num=?', (program_num, ))
  conn.commit()

def get_program_num_students(conn, program_num):
  return conn.execute(f'SELECT COUNT(*) FROM Program_Accepts WHERE program={program_num}').fetchone()[0]

def get_program_num_k12_students(conn, program_num):
  return conn.execute(f'''SELECT COUNT(*) FROM 
                    (SELECT * FROM Program_accepts WHERE program = {program_num}) AS Accepted_students
                    INNER JOIN
                    (SELECT * FROM College_students WHERE student_type = 'k12_student') AS K12_students
                    ON Accepted_students.student_num=K12_students.UIN''').fetchone()[0]

def num_students_completed_program(conn, program_num):
  return conn.execute(f'SELECT COUNT(*) FROM TRACK WHERE program = {program_num} AND status = "Completed"').fetchone()[0]

def num_in_program_and_coursetype(conn, program_num, course_type):
  return conn.execute(f'''SELECT COUNT(DISTINCT Class_enrollment.UIN) AS num_students_in_foreign_lang 
                    FROM (SELECT * FROM Program_Accepts WHERE Program = {program_num}) AS Accepted_students
                    JOIN Class_enrollment
                    ON Accepted_students.student_num = Class_enrollment.UIN
                    JOIN Classes
                    ON Class_enrollment.Class_ID = Classes.Class_ID
                    WHERE Classes.type = '{course_type}'
                    ''').fetchone()[0]

def num_w_specified_DoD_training_status(conn, program_num, status):
  return conn.execute(f'''SELECT COUNT(DISTINCT Student_num)
                    FROM Program_student_certification_data
                    WHERE program = {program_num} AND Training_Status = "{status}"
                      ''').fetchone()[0]

def num_completed_DoD_cert(conn, program_num):
  return conn.execute(f'''SELECT COUNT(DISTINCT Student_num)
                    FROM Program_student_certification_data
                    WHERE program = {program_num} AND status = "Complete"
                      ''').fetchone()[0]

def num_federal_internships(conn, program_num):
  return conn.execute(f'''SELECT COUNT(DISTINCT student_num) 
                  FROM (SELECT * FROM Program_Accepts WHERE Program = {program_num}) AS prog_students
                  JOIN (SELECT * FROM Intern_App WHERE status="Accepted") as accepted_interns
                  ON prog_students.student_num = accepted_interns.UIN
                  JOIN Internship
                  ON accepted_interns.Intern_ID = Internship.Intern_ID
                  WHERE Internship.Is_Gov = "Yes"
                    ''').fetchone()[0]
  
def names_of_prog_student_internships(conn, program_num):
  return conn.execute(f'''SELECT DISTINCT Internship.name
            FROM (SELECT * FROM Program_Accepts WHERE Program = {program_num}) AS prog_students
            JOIN (SELECT * FROM Intern_App WHERE status="Accepted") as accepted_interns
            ON prog_students.student_num = accepted_interns.UIN
            JOIN Internship
            ON accepted_interns.Intern_ID = Internship.Intern_ID
              ''').fetchall()

def get_prog_student_majors(conn, program_num):
  return conn.execute(f'''SELECT View_CollegeStudentDetails.major FROM
                    (SELECT * FROM Program_accepts WHERE program = {program_num}) AS Accepted_students
                    INNER JOIN
                    View_CollegeStudentDetails
                    ON Accepted_students.student_num = View_CollegeStudentDetails.UIN''').fetchall()

# These functions are mainly meant for student pages
def get_applied_programs(conn, UIN):
  return conn.execute(f"SELECT * FROM View_ApplicationDetails Where UIN = {UIN}").fetchall()

def update_prog_apps(conn, uncom_cert, com_cert, purpose_statement, app_num):
  conn.execute("UPDATE Application SET uncom_cert=?, com_cert=?, purpose_statement=? WHERE app_num=?"
                 , (uncom_cert, com_cert, purpose_statement, app_num))
  conn.commit()
  
  
# Freddy Queries
def addTrackRecord(conn, UIN, program_id, is_accepted):
  
  new_status = 'Enrolled' if is_accepted else 'Rejected'
  
  conn.execute("INSERT INTO Track (student_num, program, status) VALUES (?, ?, ?)", (UIN, program_id, new_status))
  conn.commit()
  
def get_all_programs_by_user(conn, UIN):
  return conn.execute('SELECT * FROM View_ApplicationDetails WHERE UIN = ?', (UIN,)).fetchall()

def updateTrackRecord(conn, UIN, program_id, new_status):
  conn.execute('UPDATE Track SET status=? WHERE program=? and student_num=?', (new_status, program_id, UIN))
  conn.commit()