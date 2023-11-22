from flask import flash
from db import *

def is_program_name_taken(conn, program_name):
  program_exist = conn.execute('SELECT COUNT(*) FROM Programs WHERE name=?', (program_name, )).fetchone()[0]
  if (program_exist > 0):
    return True
  else:
    return False
  
def add_new_program(conn, program_name, program_descr):
  conn.execute('INSERT INTO Programs (name, description) VALUES (?, ?)', (program_name, program_descr))
  conn.commit()

def get_all_programs(conn):
  return conn.execute('SELECT * FROM Programs').fetchall()