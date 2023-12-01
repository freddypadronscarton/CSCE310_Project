from flask import flash
from db import *

# VIEW ALL EVENTS
def get_all_events(conn):
    return conn.execute('SELECT * FROM Event').fetchall()

# CREATE NEW EVENT
def add_new_event(conn, Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type):
    conn.execute('INSERT INTO Event (Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type) VALUES (?, ?, ?, ?, ?, ?, ?)', (Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type))
    conn.commit()

# DELETE EVENT
def delete_event_backend(conn, Event_ID):
    conn.execute('DELETE FROM Event WHERE Event_ID=?', (Event_ID, ))
    conn.commit()