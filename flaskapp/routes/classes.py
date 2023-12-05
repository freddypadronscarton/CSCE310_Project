from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from db import *
from util.Users import *
from util.Programs import *

classes_bp = Blueprint('classes_bp', __name__)

@classes_bp.route('/view_classes/<int:UIN>', methods=['GET'])
@login_required
def view_classes(UIN):
    if current_user.user_type != "admin":
        return jsonify({"Erorr" : "Access Denied"})
    UIN = request.args.get('UIN', type=int)
    # if UIN is None:
    #     return jsonify({"Error": "UIN not provided in the URL"})
    conn = get_db_connection()
    classes = conn.execute('SELECT * FROM View_ClassEnrollmentDetails where UIN = ?', (UIN,)).fetchall()
    conn.close()
    return render_template('admin/view_classes.html', classes=classes)

@classes_bp.route('/view_all_classes', methods=['GET'])
@login_required
def view_all_classes():
    conn = get_db_connection()
    classes = conn.execute('SELECT * FROM Classes').fetchall()
    conn.close()
    return render_template('view_all_classes.html', classes=classes)

@classes_bp.route('/add_classes', methods=['GET', 'POST'])
@login_required
def add_classes():
    if(request.method == "POST"):
        class_name = request.form['class_name']
        class_descr = request.form['class_descr']
        conn = get_db_connection()
        class_exist = is_class_name_taken(conn, class_name)
        if class_exist:
            flash("A class of this name already exists")
            conn.close()
        else:
            add_new_class(conn, class_name, class_descr)
            conn.close()
            return redirect(url_for("home"))
    return render_template('add_classes.html')

@classes_bp.route('/delete_class/<int:Class_ID>', methods=['DELETE'])
@login_required
def delete_class(Class_ID):
    conn = get_db_connection()
    delete_class_backend(conn, Class_ID)
    delete_enrollments_by_class_id(conn, Class_ID)
    conn.close()
    return jsonify({"change": "program deleted"})











def is_class_name_taken(conn, class_name):
    class_exist = conn.execute('SELECT COUNT(*) FROM Classes WHERE name=?', (class_name, )).fetchone()[0]
    if (class_exist > 0):
        return True
    else:
        return False

def get_class_by_name(conn, class_name):
    if is_class_name_taken(conn, class_name):
        return conn.execute('SELECT * FROM Classes WHERE name=?', (class_name, )).fetchone()
    else:
        return None

def add_new_class(conn, class_name, class_descr):
  conn.execute('INSERT INTO Classes (name, description) VALUES (?, ?)', (class_name, class_descr))
  conn.commit()

def enroll_class(conn, class_name, class_descr):
    class_ = get_class_by_name(conn, class_name)
    if class_ is None:
        conn.execute('INSERT INTO Classes (name, description) VALUES (?, ?)', (class_name, class_descr))
        class_ = get_class_by_name(conn, class_name)
    conn.execute('INSERT INTO Class_Enrollment (UIN, Class_ID, Status, Semester, Year) VALUES (?, ?, "Enrolled", 0, 0)', (current_user.uin, class_['Class_ID']))
    conn.commit()
    
def get_all_classes_by_user(conn, UIN):
    return conn.execute('SELECT * FROM View_ClassEnrollmentDetails where UIN = ?', (UIN,)).fetchall()
    
def delete_class_backend(conn, Class_ID):
  conn.execute('DELETE FROM Classes WHERE Class_ID=?', (Class_ID, ))
  conn.commit()

def delete_enrollments_by_class_id(conn, Class_ID):
    conn.execute('DELETE FROM Class_Enrollment WHERE Class_ID=?', (Class_ID,))
    conn.commit()
