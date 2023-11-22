# admin.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from db import *
from util.Users import *

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
        print(program_name)
        conn = get_db_connection()
        program_exist = conn.execute('SELECT COUNT(*) FROM Programs WHERE name=?', (program_name, )).fetchone()[0]
        if (program_exist > 0):
            flash("A program of this name already exists")
        else:
            conn.execute('INSERT INTO Programs (name, description) VALUES (?, ?)', (program_name, program_descr))
            conn.commit()
        conn.close()
        return render_template("admin_home.html")
    else:
      return render_template("admin_add_program.html")