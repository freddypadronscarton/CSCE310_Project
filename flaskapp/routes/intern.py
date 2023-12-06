from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from db import *
from util.Users import *
from util.Programs import *

intern_bp = Blueprint('intern_bp', __name__)

@intern_bp.route('/add_internship_student/<int:UIN>', methods=['GET', 'POST'])
@login_required
def add_internship_student(UIN):
    if(request.method == "POST"):
        intern_name = request.form['intern_name']
        intern_descr = request.form['intern_descr']
        intern_year = request.form['intern_year']
        intern_status = request.form['intern_status']
        intern_isGov = request.form['intern_isGov']
        conn = get_db_connection()
        intern_exist = get_intern_by_name(conn, intern_name)
        if intern_exist:
            intern_app = get_intern_app(conn, intern_exist['Intern_ID'], UIN)
            if intern_app:
                flash("An internship of this name already exists")
            conn.close()
        else:
            enroll_intern(conn, intern_name, intern_descr, intern_isGov, intern_year, intern_status, UIN)
            conn.close()
            return redirect(url_for("intern_bp.view_internships.html", UIN=UIN))
    return render_template('add_internship_student.html')

@intern_bp.route('/add_internship/<int:UIN>', methods=['GET', 'POST'])
@login_required
def add_internship(UIN):
    if(request.method == "POST"):
        intern_name = request.form['intern_name']
        intern_descr = request.form['intern_descr']
        intern_year = request.form['intern_year']
        intern_status = request.form['intern_status']
        intern_isGov = request.form['intern_isGov']
        conn = get_db_connection()
        intern_exist = is_intern_name_taken(conn, intern_name)
        if intern_exist:
            flash("An internship of this name already exists")
            conn.close()
        else:
            enroll_intern(conn, intern_name, intern_descr, intern_isGov, intern_year, intern_status, UIN)
            conn.close()
            return redirect(url_for("progress_bp.view_progress", UIN=UIN))
    return render_template('admin/admin_add_internship.html')

@intern_bp.route('/view_internships/<int:UIN>', methods=['GET'])
@login_required
def view_internships(UIN):
    conn = get_db_connection()
    intern = get_all_interns_by_user(conn, UIN)
    name = conn.execute('SELECT First_Name FROM Users WHERE UIN=?', (UIN,)).fetchone()
    conn.close()
    return render_template('admin/view_internships.html', interns=intern, name=name['First_Name'])

@intern_bp.route('/view_all_internships', methods=['GET'])
@login_required
def view_all_internships():
    conn = get_db_connection()
    intern = conn.execute('SELECT * FROM Internship').fetchall()
    conn.close()
    return render_template('admin/view_all_internships.html', interns=intern)

@intern_bp.route('/update_intern_basic/<int:Intern_ID>', methods=['GET', 'POST'])
@login_required
def update_intern_basic(Intern_ID):
    conn = get_db_connection()
    if (request.method == 'POST'):
        update_intern_info(conn, Intern_ID, request.form["intern_name"], request.form["intern_descr"], request.form["intern_isGov"])
        conn.close()
        return redirect(url_for('intern_bp.view_all_internships'))
    intern = get_intern_by_id(conn, Intern_ID)
    conn.close()
    return render_template("admin/update_intern_basic.html", intern=intern)

@intern_bp.route('/update_intern/<int:Intern_ID>/<int:UIN>', methods=['GET', 'POST'])
@login_required
def update_intern(Intern_ID, UIN):
    conn = get_db_connection()
    if (request.method == 'POST'):
        update_intern_info(conn, Intern_ID, request.form["intern_name"], request.form["intern_descr"], request.form["intern_isGov"])
        update_intern_app_info(conn, Intern_ID, UIN, request.form["intern_status"], request.form["intern_year"])
        conn.close()
        return redirect(url_for('progress_bp.view_progress', UIN=UIN))
    intern = get_intern_by_id(conn, Intern_ID)
    intern_app = get_intern_app(conn, Intern_ID, UIN)
    conn.close()
    return render_template("admin/update_intern.html", intern=intern, intern_app=intern_app)

@intern_bp.route('/update_intern_student/<int:Intern_ID>/<int:UIN>', methods=['GET', 'POST'])
@login_required
def update_intern_student(Intern_ID, UIN):
    conn = get_db_connection()
    if (request.method == 'POST'):
        update_intern_app_info(conn, Intern_ID, UIN, request.form["intern_status"], request.form["intern_year"])
        conn.close()
        return redirect(url_for('intern_bp.view_internships', UIN=UIN))
    intern = get_intern_by_id(conn, Intern_ID)
    intern_app = get_intern_app(conn, Intern_ID, UIN)
    conn.close()
    return render_template("student/update_intern_student.html", intern=intern, intern_app=intern_app)

@intern_bp.route('/delete_intern_student/<int:Intern_ID>/<int:UIN>', methods=['DELETE'])
@login_required
def delete_intern_student(Intern_ID, UIN):
    conn = get_db_connection()
    delete_enrollments_by_intern_id_and_uin(conn, Intern_ID, UIN)
    conn.close()
    return jsonify({"change": "program deleted"})

@intern_bp.route('/delete_intern/<int:Intern_ID>', methods=['DELETE'])
@login_required
def delete_intern(Intern_ID):
    conn = get_db_connection()
    delete_intern_backend(conn, Intern_ID)
    delete_enrollments_by_intern_id(conn, Intern_ID)
    conn.close()
    return jsonify({"change": "program deleted"})



##################################################### FUNCTIONS #####################################################

def is_intern_name_taken(conn, intern_name):
    intern_exist = conn.execute('SELECT COUNT(*) FROM Internship WHERE name=?', (intern_name, )).fetchone()[0]
    return (intern_exist > 0)

def get_intern_by_name(conn, intern_name):
    if is_intern_name_taken(conn, intern_name):
        return conn.execute('SELECT * FROM Internship WHERE name=?', (intern_name, )).fetchone()
    else:
        return None

def get_intern_by_id(conn, intern_id):
    return conn.execute('SELECT * FROM Internship WHERE Intern_ID=?', (intern_id,)).fetchone()

def get_all_interns_by_user(conn, UIN):
    return conn.execute('SELECT * FROM View_InternAppDetails where UIN = ?', (UIN,)).fetchall()

def get_intern_app(conn, intern_id, UIN):
    return conn.execute('SELECT * FROM Intern_App WHERE Intern_ID=? AND UIN=?', (intern_id, UIN)).fetchone()


def add_new_intern(conn, intern_name, intern_descr, intern_isGov):
  conn.execute('INSERT INTO Internship (name, description, Is_Gov) VALUES (?, ?, ?)', (intern_name, intern_descr, intern_isGov))
  conn.commit()

def enroll_intern(conn, intern_name, intern_descr, intern_isGov, year, status, UIN):
    intern = get_intern_by_name(conn, intern_name)
    if intern is None:
        add_new_intern(conn, intern_name, intern_descr, intern_isGov)
        intern = get_intern_by_name(conn, intern_name)
    conn.execute('INSERT INTO Intern_App (UIN, Intern_ID, Status, Year) VALUES (?, ?, ?, ?)', (UIN, intern['Intern_ID'], status, year))
    conn.commit()

def update_intern_info(conn, intern_id, intern_name, intern_descr, intern_isGov):
    conn.execute('UPDATE Internship SET name=?, description=?, Is_Gov=? WHERE Intern_ID=?', (intern_name, intern_descr, intern_isGov, intern_id))
    conn.commit()

def update_intern_app_info(conn, intern_id, UIN, status, year):
    print("updating intern app info")
    print(f"Intern_ID: {intern_id} UIN: {UIN}")
    print(f"status: {status} year: {year}")
    conn.execute('UPDATE Intern_App SET status=?, year=? WHERE UIN=? AND Intern_ID=?', (status, year, UIN, intern_id))
    conn.commit()

def delete_intern_backend(conn, Intern_ID):
  conn.execute('DELETE FROM Internship WHERE Intern_ID=?', (Intern_ID, ))
  conn.commit()

def delete_enrollments_by_intern_id(conn, Intern_ID):
    conn.execute('DELETE FROM Intern_App WHERE Intern_ID=?', (Intern_ID, ))
    conn.commit()

def delete_enrollments_by_intern_id_and_uin(conn, Intern_ID, UIN):
    conn.execute('DELETE FROM Intern_App WHERE Intern_ID=? AND UIN=?', (Intern_ID, UIN))
    conn.commit()