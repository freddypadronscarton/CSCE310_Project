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
    conn = get_db_connection()
    classes = get_all_classes_by_user(conn, UIN)
    conn.close()
    return render_template('admin/view_classes.html', classes=classes)

@classes_bp.route('/view_all_classes', methods=['GET'])
@login_required
def view_all_classes():
    print("called view_all_classes")
    conn = get_db_connection()
    classes = conn.execute('SELECT * FROM Classes').fetchall()
    conn.close()
    return render_template('view_all_classes.html', classes=classes)

@classes_bp.route('/add_classes/<int:UIN>', methods=['GET', 'POST'])
@login_required
def add_classes(UIN):
    if(request.method == "POST"):
        class_name = request.form['class_name']
        class_descr = request.form['class_descr']
        class_type = request.form['class_type']
        class_semester = request.form['class_semester']
        class_year = request.form['class_year']
        class_status = request.form['class_status']
        conn = get_db_connection()
        class_exist = is_class_name_taken(conn, class_name)
        if class_exist:
            flash("A class of this name already exists")
            conn.close()
        else:
            enroll_class(conn, class_name, class_descr, class_type, class_semester, class_year, class_status, UIN)
            conn.close()
            return redirect(url_for("progress_bp.view_progress", UIN=UIN))
    return render_template('add_classes.html')

@classes_bp.route('/delete_class/<int:Class_ID>', methods=['DELETE'])
@login_required
def delete_class(Class_ID):
    conn = get_db_connection()
    delete_class_backend(conn, Class_ID)
    delete_enrollments_by_class_id(conn, Class_ID)
    conn.close()
    return jsonify({"change": "program deleted"})

@classes_bp.route('/update_class/<int:Class_ID>/<int:UIN>', methods=['GET', 'POST'])
@login_required
def update_class(Class_ID, UIN):
    print(request.form)
    print(request.method)
    conn = get_db_connection()
    if (request.method == 'POST'):
        update_class_info(conn, Class_ID, request.form["class_name"], request.form["class_descr"], request.form["class_type"])
        update_enrollment_info(conn, Class_ID, UIN, request.form["class_semester"], request.form["class_year"], request.form["class_status"])
        conn.close()
        return redirect(url_for('progress_bp.view_progress', UIN=UIN))
        # return redirect(url_for('classes_bp.update_class', Class_ID=Class_ID, UIN=UIN))
    class_ = get_class_by_id(conn, Class_ID)
    enrollment = get_enrollment(conn, Class_ID, UIN)
    conn.close()
    return render_template("admin/update_class.html", class_=class_, enrollment=enrollment)


@classes_bp.route('/update_class_basic/<int:Class_ID>', methods=['GET', 'POST'])
@login_required
def update_class_basic(Class_ID):
    print(request.form)
    print(request.method)
    conn = get_db_connection()
    if (request.method == 'POST'):
        update_class_info(conn, Class_ID, request.form["class_name"], request.form["class_descr"], request.form["class_type"])
        conn.close()
        return redirect(url_for('classes_bp.view_all_classes'))
        # return redirect(url_for('classes_bp.update_class_basic', Class_ID=Class_ID, UIN=UIN))
    class_ = get_class_by_id(conn, Class_ID)
    conn.close()
    return render_template("admin/update_class_basic.html", class_=class_)

@classes_bp.route('/update_class_student/<int:Class_ID>/<int:UIN>', methods=['GET', 'POST'])
@login_required
def update_class_student(Class_ID, UIN):
    print(request.form)
    print(request.method)
    conn = get_db_connection()
    if (request.method == 'POST'):
        # update_class_info(conn, Class_ID, request.form["class_name"], request.form["class_descr"], request.form["class_type"])
        update_enrollment_info(conn, Class_ID, UIN, request.form["class_semester"], request.form["class_year"], request.form["class_status"])
        conn.close()
        return redirect(url_for('classes_bp.view_classes', UIN=UIN))
        # return redirect(url_for('classes_bp.update_class', Class_ID=Class_ID, UIN=UIN))
    class_ = get_class_by_id(conn, Class_ID)
    enrollment = get_enrollment(conn, Class_ID, UIN)
    conn.close()
    return render_template("student/update_class_student.html", class_=class_, enrollment=enrollment)







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

def get_class_by_id(conn, class_id):
    return conn.execute('SELECT * FROM Classes WHERE Class_ID=?', (class_id,)).fetchone()
    
def get_enrollment(conn, class_id, UIN):
    return conn.execute('SELECT * FROM Class_Enrollment WHERE Class_ID=? AND UIN=?', (class_id, UIN)).fetchone()

def add_new_class(conn, class_name, class_descr, class_type):
  conn.execute('INSERT INTO Classes (name, description, type) VALUES (?, ?, ?)', (class_name, class_descr, class_type))
  conn.commit()

def enroll_class(conn, class_name, class_descr, class_type, semester, year, status, UIN):
    class_ = get_class_by_name(conn, class_name)
    if class_ is None:
        add_new_class(conn, class_name, class_descr, class_type)
        class_ = get_class_by_name(conn, class_name)
    conn.execute('INSERT INTO Class_Enrollment (UIN, Class_ID, Status, Semester, Year) VALUES (?, ?, ?, ?, ?)', (UIN, class_['Class_ID'], status, semester, year))
    conn.commit()
    
def get_all_classes_by_user(conn, UIN):
    return conn.execute('SELECT * FROM View_ClassEnrollmentDetails where UIN = ?', (UIN,)).fetchall()
    
def delete_class_backend(conn, Class_ID):
  conn.execute('DELETE FROM Classes WHERE Class_ID=?', (Class_ID, ))
  conn.commit()

def delete_enrollments_by_class_id(conn, Class_ID):
    conn.execute('DELETE FROM Class_Enrollment WHERE Class_ID=?', (Class_ID,))
    conn.commit()

def update_class_info(conn, class_id, class_name, class_descr, class_type):
    conn.execute('UPDATE Classes SET name=?, description=?, type=? WHERE Class_ID=?', (class_name, class_descr, class_type, class_id))
    conn.commit()

def update_enrollment_info(conn, class_id, UIN, class_semester, class_year, class_status):
    conn.execute('UPDATE Class_Enrollment SET Semester=?, Year=?, Status=? WHERE Class_ID=?', (class_semester, class_year, class_status, class_id))
    conn.commit()
