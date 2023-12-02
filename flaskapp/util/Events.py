from flask import flash
from db import *

# VIEW ALL EVENTS
def get_all_events(conn):
    return conn.execute('SELECT * FROM Event').fetchall()

# GET EVENT BY ID
def get_event(conn, Event_ID):
    return conn.execute('SELECT * FROM Event WHERE Event_ID=?', (Event_ID, )).fetchone()

# CREATE NEW EVENT
def add_new_event(conn, Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type):
    conn.execute('INSERT INTO Event (Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type) VALUES (?, ?, ?, ?, ?, ?, ?)', (Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type))
    conn.commit()

# DELETE EVENT
def delete_event_backend(conn, Event_ID):
    conn.execute('DELETE FROM Event WHERE Event_ID=?', (Event_ID, ))
    conn.commit()

# UPDATE EVENT
def update_event_info(conn, Event_ID, Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type):
    conn.execute('UPDATE Event SET Program_Num=?, UIN=?, Start_Date=?, Time=?, Location=?, End_Date=?, Event_Type=? WHERE Event_ID=?', (Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type, Event_ID))
    conn.commit()

# VIEW ALL STUDENTS CONNECTED TO AN EVENT
def get_students_by_event(conn, Event_ID):
    return conn.execute('SELECT * FROM Event_Tracking WHERE Event_ID=?', (Event_ID, )).fetchall()

# GET NUMBER OF STUDENTS CONNECTED TO AN EVENT
def get_event_attendance(conn, Event_ID):
    return conn.execute('SELECT COUNT(*) FROM Event_Tracking WHERE Event_ID=?', (Event_ID, )).fetchone()

# ADD STUDENT TO EVENT
def add_student_to_event(conn, Event_ID, UIN):
    conn.execute('INSERT INTO Event_Tracking (Event_ID, UIN) VALUES (?, ?)', (Event_ID, UIN))
    conn.commit()