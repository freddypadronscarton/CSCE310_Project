from flask import flash
from db import *
import os

# VIEW ALL DOCUMENTS
def get_all_documents(conn):
    return conn.execute('SELECT * FROM Documents').fetchall()

# VIEW DOCUMENTS BY ID
def get_document_by_id(conn, id):
    return conn.execute('SELECT * FROM Documents WHERE Doc_Num = ?', (id,)).fetchone()

# CREATE DOCUMENT
def create_document(conn, app_num, link, type):
    conn.execute('INSERT INTO Documents (App_Num, Link, Doc_Type) VALUES (?, ?, ?)', (app_num, link, type))
    conn.commit()

# DELETE DOCUMENT
def delete_document_backend(conn, id):
    conn.execute('DELETE FROM Documents WHERE Doc_Num = ?', (id,))
    conn.commit()

# UPDATE DOCUMENT
def update_document_backend(conn, id, app_num, link, type):
    conn.execute('UPDATE Documents SET App_Num = ?, Link = ?, Doc_Type = ? WHERE Doc_Num = ?', (app_num, link, type, id))
    conn.commit()