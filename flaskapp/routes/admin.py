# admin.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from db import *
from util.Users import *
from util.Programs import *

admin_bp = Blueprint('admin_bp', __name__)

# ENDPOINT FOR ARCHIVED BUTTON
@admin_bp.route('/update_user/<int:UIN>', methods=['PUT'])
@login_required
def update_user(UIN):
    data = request.get_json()
    conn = get_db_connection()
    update_user_field(conn, UIN, data['field'], data['value'])
    conn.commit()
    conn.close()
    return jsonify({'message': 'User archived'})


# ENDPOINT FOR DELETE BUTTON
@admin_bp.route('/delete_user/<int:UIN>', methods=['DELETE'])
@login_required
def delete_user(UIN):
    conn = get_db_connection()
    delete_user(conn, UIN)
    conn.commit()
    conn.close()
        
    print("Deleted User: ", UIN)
    return jsonify({'success': 'User Deleted'})

# ENDPOINT FOR SELECTING USER TYPE
@admin_bp.route('/user_type_form', methods=['POST'])
@login_required
def user_type_form():
    user_type = request.form['user_type']
    UIN = request.form['uin']

    conn = get_db_connection()
    selected_user = conn.execute('SELECT * FROM users where UIN = ?', (UIN,)).fetchone() 
    return render_template('forms/changeUserTypeForm.html', selected_user= selected_user, user_type= user_type, current_year=datetime.now().year)

# ENDPOINT FOR USER TYPE SAVE/PROMOTE BUTTON
@admin_bp.route('/save_user_type', methods=['POST'])
@login_required
def save_user_type():
    new_user_type = request.form["user_type"]
    UIN = request.form["uin"]
    user_info = request.form
    
    # Connect to db
    conn = get_db_connection()
    
    # update user type
    update_user_field(conn, UIN, 'User_Type', new_user_type)
    
    
    # remove from student table
    delete_student(conn, UIN)
    
    # add updated information to student table
    if new_user_type == "k12_student":
        create_k12_student(conn, user_info)
    
    if new_user_type == "college_student":
        create_college_student(conn, user_info)
        
    conn.commit()
    conn.close()
    
    return redirect(url_for('home'))

# ENDPOINT FOR ADDING PROGRAMS
@admin_bp.route('/add_program', methods=['GET', 'POST'])
@login_required
def add_program():
    if (request.method == "POST"):
        program_name = request.form['program_name']
        program_descr = request.form['program_descr']
        conn = get_db_connection()
        program_exist = is_program_name_taken(conn, program_name)
        if program_exist:
            flash("A program of this name already exists")
            conn.close()
        else:
            add_new_program(conn, program_name, program_descr)
            conn.close()
            return render_template("admin_home.html")
    return render_template("admin_add_program.html")
    
# ENDPOINT FOR ADMIN TO VIEW ALL PROGRAMS
@admin_bp.route('/view_programs', methods=['GET'])
@login_required
def view_all_programs():
    conn = get_db_connection()
    programs = get_all_programs(conn)
    conn.close()
    return render_template("admin_view_programs.html", programs=programs)
  
# ENDPOINT FOR ARCHIVING AND UNARCHIVING PROGRAMS
@admin_bp.route('/archive_program', methods=['PUT'])
@login_required
def archive_program():
    data = request.get_json()
    conn = get_db_connection()
    update_program_archive_status(conn, data["program_num"], data["archive"])
    conn.close()
    return jsonify({"user archive status": data["archive"]})

# ENDPOINT FOR DELETING A PROGRAM
@admin_bp.route('/delete_program/<int:program_num>', methods=['DELETE'])
@login_required
def delete_program(program_num):
    conn = get_db_connection()
    delete_program_backend(conn, program_num)
    conn.close()
    return jsonify({"change": "program deleted"})

# ENDPOINT FOR UPDATING A PROGRAM
@admin_bp.route('/update_program/<int:program_num>', methods=['GET', 'POST'])
@login_required
def update_program(program_num):
    conn =  get_db_connection()
    if (request.method == 'POST'):
        update_program_info(conn, program_num, request.form["program_name"], request.form["program_descr"])
        conn.close()
        return redirect(url_for('admin_bp.view_all_programs'))
    program = get_program(conn, program_num)
    conn.close()
    return render_template("admin_update_program.html", program=program)