from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
from db import *
from util.Documents import *
from util.Users import *
from util.Programs import *
from util.Events import *

# FILE AUTHOR: Kelvin Zheng

application_bp = Blueprint('application_bp', __name__)


# Program Application Management Pages
@application_bp.route('/program_application')
def program_application(): 
    conn = get_db_connection()
    programs = get_all_unarchived_programs(conn)
    conn.close()
    return render_template('student/program_application.html', programs=programs)

# This is the endpoint for checking if a user has already applied to the program
@application_bp.route('/program_applied_check/<int:program_num>')
def check_if_already_applied(program_num):
    conn = get_db_connection()
    alreadyApplied = conn.execute("SELECT COUNT(*) FROM Application WHERE Program_Num = ? AND UIN = ?", (program_num, current_user.uin)).fetchone()[0]
    conn.close()
    if (alreadyApplied > 0):
        return jsonify({'alreadyApplied': True})
    else:
        return jsonify({'alreadyApplied': False})
    
@application_bp.route('/program_application', methods=['POST'])
def add_new_application():
    program_num = request.form['program_num']
    uncom_cert = request.form['uncom_cert']
    com_cert = request.form['com_cert']
    purpose_statement = request.form['purpose_statement']
    file = request.files['document']
    doc_type = request.form['document_type']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Application (program_num, UIN, uncom_cert, com_cert, purpose_statement) VALUES (?, ?, ?, ?, ?)',
                (program_num, current_user.uin, uncom_cert, com_cert, purpose_statement))
    conn.commit()
    
    # Retrieve the last inserted row ID (app_num)
    last_inserted_app_num = cursor.lastrowid
    
    if file and not doc_type == "None":
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file_path = generateFilePath(file_path)
        file.save(file_path)
        create_document(conn, last_inserted_app_num, file_path, doc_type, file.filename)
        
    flash("Application Submitted!")
    
    programs = get_all_programs(conn)
    conn.close()
    return render_template('student/program_application.html', programs=programs)


@application_bp.route('/application_review')
def application_review():
    conn = get_db_connection()
    applied_programs = get_applied_programs(conn, current_user.uin)
    conn.close()

    return render_template('student/application_review.html', applied_programs=applied_programs)
    
@application_bp.route('/update_program_app/<int:app_num>')
def load_update_appl_page(app_num):
    conn = get_db_connection()
    app = conn.execute("SELECT * FROM Application WHERE APP_NUM = ?", (app_num, )).fetchone()
    doc = conn.execute("SELECT * FROM Documents WHERE App_Num = ?", (app_num, )).fetchone()
    conn.close()
    return render_template("student/update_program_app.html", app=app, doc=doc)

@application_bp.route('/update_application', methods=['POST'])
def update_application():
    # gets all needed data from form
    app_num = request.form["app_num"]
    uncom_cert = request.form["uncom_cert"]
    com_cert = request.form["com_cert"]
    purpose_statement = request.form["purpose_statement"]

    # calls Program.py function to update program applications
    conn = get_db_connection()
    update_prog_apps(conn, uncom_cert, com_cert, purpose_statement, app_num)
    
    if request.files:
        file = request.files["document"]
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file_path = generateFilePath(file_path)
        file.save(file_path)
        create_document(conn, app_num, file_path, request.form["document_type"], file.filename)
    
    conn.close()
    return redirect(url_for('application_bp.application_review'))

# deletes a user's application and deletes the user from the program track
# a user deleting their application means they are leaving the program
@application_bp.route('/delete_application/<int:app_num>', methods=['DELETE'])
def delete_application(app_num):
  conn = get_db_connection()
  program_num = conn.execute(f"SELECT program_num FROM Application where app_num = {app_num}").fetchone()[0]
  uin = conn.execute(f"SELECT UIN FROM Application where app_num = {app_num}").fetchone()[0]
  print(program_num)
  print(uin)
  conn.execute(f"DELETE FROM Application WHERE app_num = {app_num}")
  conn.execute(f"DELETE FROM TRACK WHERE program = {program_num} AND student_num = {uin}")
  delete_document_by_app_num(conn, app_num)
  conn.commit()
  conn.close()
  return jsonify({"success": "program application deleted"})
  