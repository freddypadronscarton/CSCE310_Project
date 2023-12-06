from flask import flash
from db import *
import os

# VIEW ALL DOCUMENTS
def get_all_documents(conn):
    return conn.execute('SELECT * FROM View_DocumentsApplicationPrograms').fetchall()

# VIEW DOCUMENTS BY ID
def get_document_by_id(conn, id):
    return conn.execute('SELECT * FROM View_DocumentsApplicationPrograms WHERE Doc_Num = ?', (id,)).fetchone()

# CREATE DOCUMENT
def create_document(conn, app_num, link, type, file_name):
    conn.execute('INSERT INTO Documents (App_Num, Link, Doc_Type, Name) VALUES (?, ?, ?, ?)', (app_num, link, type, file_name))
    conn.commit()

# DELETE DOCUMENT
def delete_document_backend(conn, id):
    conn.execute('DELETE FROM Documents WHERE Doc_Num = ?', (id,))
    conn.commit()

# UPDATE DOCUMENT
def update_document_backend(conn, id, app_num, link, type, name):
    conn.execute('UPDATE Documents SET App_Num = ?, Link = ?, Doc_Type = ?, Name = ? WHERE Doc_Num = ?', (app_num, link, type, name, id))
    print('UPDATE Documents SET App_Num = ?, Link = ?, Doc_Type = ?, Name = ? WHERE Doc_Num = ?')
    conn.commit()
    
    
def generateFilePath(file_path):
    while os.path.exists(file_path):
        name, ext = os.path.splitext(file_path)
        
        if ' - copy' in name:
            # If the file already has ' - copy', increment the copy number
            parts = name.split(' - copy')
            if parts[-1].isdigit():
                number = int(parts[-1]) + 1
                name = ' - copy'.join(parts[:-1]) + ' - copy' + str(number)
            else:
                name += ' - copy2'
        else:
            # First time adding ' - copy'
            name += ' - copy'
            
        file_path = name + ext
    
    return file_path