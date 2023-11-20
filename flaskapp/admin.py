# admin.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from db import *

admin_bp = Blueprint('admin_bp', __name__)


# ENDPOINT FOR ARCHIVED BUTTON
@admin_bp.route('/update_user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    update_user_field(user_id, data['field'], data['value'])
    return jsonify({'message': 'User archived'})


# ENDPOINT FOR DELETE BUTTON
@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    try:
        conn = get_db_connection()
        
        conn.execute(f"DELETE FROM students WHERE user_id = {user_id}")
        conn.execute(f"DELETE FROM k12_students WHERE user_id = {user_id}")
        conn.execute(f"DELETE FROM college_students WHERE user_id = {user_id}")
        conn.execute(f"DELETE FROM admins WHERE user_id = {user_id}")
        conn.execute(f"DELETE FROM users WHERE user_id = {user_id}")
        
    except Exception as e:
        return jsonify({'error': 'Deletion failed'})
    
    conn.commit()
    conn.close()
        
    print("Deleted User: ", user_id)
    return jsonify({'success': 'User Deleted'})

# ENDPOINT FOR SELECTING USER TYPE
@admin_bp.route('/user_type_form', methods=['POST'])
@login_required
def user_type_form():
    user_type = request.form['user_type']
    user_id = request.form['user_id']

    conn = get_db_connection()
    selected_user = conn.execute('SELECT * FROM users where user_id = ?', (user_id,)).fetchone() 
    return render_template('forms/changeUserTypeForm.html', selected_user= selected_user, user_type= user_type)

# ENDPOINT FOR USER TYPE SAVE BUTTON
@admin_bp.route('/save_user_type', methods=['POST'])
@login_required
def update_user_type():
    new_user_type = request.form["user_type"]
    user_id = request.form["user_id"]
    
    # Connect to db
    conn = get_db_connection()
    
    # Remove user_id from subtype tables
    conn.execute(f"DELETE FROM students WHERE user_id = {user_id}")
    conn.execute(f"DELETE FROM k12_students WHERE user_id = {user_id}")
    conn.execute(f"DELETE FROM college_students WHERE user_id = {user_id}")
    conn.execute(f"DELETE FROM admins WHERE user_id = {user_id}")
    
    print(request.form)
    
    if new_user_type == "admin":
        # Insert into new subtype table
        conn.execute('INSERT INTO admins (user_id, title, authenticated) VALUES (?, ?, ?)',
                        (user_id, request.form["title"], 1))
        
        # update type in users table
        update_user_field(conn, user_id, 'student_type', None)
        update_user_field(conn, user_id, 'is_admin', "True")
    elif new_user_type == "k12_student":
        # Insert into new subtype tables
        conn.execute('INSERT INTO students (user_id, in_college, US_citizen) VALUES (?, ?, ?)',
                        (user_id, "False", "True" if "US_citizen" in request.form else "False"))

        conn.execute('INSERT INTO k12_students (user_id, grade) VALUES (?, ?)',
                        (user_id, request.form["grade"]))
        
        # update type in users table
        update_user_field(conn, user_id, 'student_type', new_user_type)
        update_user_field(conn, user_id, 'is_admin', "False")
        
    elif new_user_type == "college_student":      
        # add to students table
        conn.execute('INSERT INTO students (user_id, in_college, US_citizen) VALUES (?, ?, ?)',
                        (user_id, "True", "True" if "US_citizen" in request.form else "False"))
        
        # add to college_students table
        conn.execute('INSERT INTO college_students (user_id, UIN, first_gen, classification, major, second_major, minor, second_minor, gpa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (user_id, request.form["uin"], "True" if "first_gen" in request.form else "False", request.form["classification"], request.form["major"], request.form["second_major"], request.form["minor"], request.form["second_minor"], request.form["gpa"]))
    
        # update type in users table
        update_user_field(conn, user_id, 'student_type', new_user_type)
        update_user_field(conn, user_id, 'is_admin', "False")
        
        
    conn.commit()
    conn.close()
    
    return redirect(url_for('home'))