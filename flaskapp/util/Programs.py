from flask import flash
from db import *

def is_program_name_taken(conn, program_name):
  program_exist = conn.execute('SELECT COUNT(*) FROM Programs WHERE name=?', (program_name, )).fetchone()[0]
  if (program_exist > 0):
    return True
  else:
    return False
  
def add_new_program(conn, program_name, program_descr):
  conn.execute('INSERT INTO Programs (name, description, archived) VALUES (?, ?, 0)', (program_name, program_descr))
  conn.commit()

def get_program(conn, program_num):
  return conn.execute('SELECT * FROM Programs WHERE program_num=?', (program_num, )).fetchone()

def get_all_programs(conn):
  return conn.execute('SELECT * FROM Programs').fetchall()

def update_program_info(conn, program_num, program_name, program_descr):
  conn.execute('UPDATE Programs SET name=?, description=? WHERE program_num=?', (program_name, program_descr, program_num))
  conn.commit()

def update_program_archive_status(conn, program_num, archived):
  conn.execute('UPDATE Programs SET archived=? WHERE program_num=?', (archived, program_num))
  conn.commit()

def delete_program_backend(conn, program_num):
  conn.execute('DELETE FROM Programs WHERE program_num=?', (program_num, ))
  conn.commit()

def get_applied_programs(conn, UIN):
  return conn.execute(f'''SELECT * FROM View_ApplicationDetails Where UIN = {UIN}''').fetchall()

def update_prog_apps(conn, uncom_cert, com_cert, purpose_statement, app_num):
  conn.execute("UPDATE Application SET uncom_cert=?, com_cert=?, purpose_statement=? WHERE app_num=?"
                 , (uncom_cert, com_cert, purpose_statement, app_num))
  conn.commit()