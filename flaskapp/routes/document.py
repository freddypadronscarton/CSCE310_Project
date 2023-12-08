from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
from db import *
from util.Documents import *
from util.Users import *
from util.Programs import *
from util.Events import *

# File author : Christian Jeardoe

document_bp = Blueprint('document_bp', __name__)

@document_bp.route('/display')
def document_display():
    conn = get_db_connection()
    documents = get_all_documents(conn)
    conn.close()
    return render_template('student/document_display.html' , documents=documents)

@document_bp.route('/upload_document', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        app_num = request.form['app_num']
        type = request.form['type']
        file = request.files['document']
        if file:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            file_path = generateFilePath(file_path)
            file.save(file_path)
            conn = get_db_connection()
            create_document(conn, app_num, file_path, type, file.filename)
            conn.close()

            return redirect(url_for('document_bp.document_display'))

    return render_template('upload_document.html')


@document_bp.route('/delete_document/<int:doc_num>', methods=['DELETE'])
def delete_document(doc_num):
    conn = get_db_connection()
    document = get_document_by_id(conn, doc_num)
    delete_document_backend(conn, doc_num)
    os.remove(document['Link'])
    conn.close()
    return jsonify({"success": "document deleted"})

@document_bp.route('/update_document/<int:doc_num>', methods=['GET', 'POST'])
def update_document(doc_num):
    conn = get_db_connection()
    document = get_document_by_id(conn, doc_num)
    conn.close()
    return render_template('student/update_document.html', document=document)

@document_bp.route('/update_file/<int:doc_num>', methods=['POST'])
def update_file(doc_num):
    conn = get_db_connection()
    oldDoc = get_document_by_id(conn, doc_num)
    
    app_num = oldDoc['app_num']
    type = request.form['document_type']
    file = request.files['document']
    if file:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file.save(generateFilePath(file_path))
        os.remove(oldDoc['Link'])
        update_document_backend(conn, doc_num, app_num, file_path, type, file.filename)


    conn.close()
    return redirect(url_for('document_bp.document_display'))