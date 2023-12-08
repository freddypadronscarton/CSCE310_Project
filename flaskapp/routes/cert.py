#cert.py - Alex Kilgorea
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from db import *
from util.Users import *
from util.Programs import *


cert_bp = Blueprint('cert_bp', __name__)

# Endpoint for viewing addable certifications
# Actual db changes happen in enroll_cert
@cert_bp.route('/add_cert/<int:UIN>', methods=['GET'])
@login_required
def add_cert(UIN):
    conn = get_db_connection()
    certs = get_user_unenrolled_certs(conn, UIN)
    conn.close()
    return render_template('admin/view_certs.html', certs=certs,  flag="add")


# Endpoint for viewing user's enrolled certifications
# Actual db changes happen in remove_cert
@cert_bp.route('/view_cert/<int:UIN>', methods=['GET'])
@login_required
def view_cert(UIN):
    conn = get_db_connection()
    certs = get_user_enrolled_certs(conn, UIN)
    name = conn.execute('SELECT First_Name FROM Users WHERE UIN=?', (UIN,)).fetchone()
    conn.close()
    return render_template('admin/view_certs.html', certs=certs, name=name['First_Name'], flag="view")


@cert_bp.route('/enroll_cert/<int:Cert_ID>/<int:UIN>', methods=['GET', 'POST'])
@login_required
def enroll_cert(UIN, Cert_ID):
    conn = get_db_connection()
    create_cert_enrollment(conn, UIN, Cert_ID)
    conn.close()
    return redirect(url_for('cert_bp.update_cert_enrollment', UIN=UIN, Cert_ID=Cert_ID))


@cert_bp.route('/update_cert_enrollment/<int:Cert_ID>/<int:UIN>', methods=['GET', 'POST'])
@login_required
def update_cert_enrollment(UIN, Cert_ID):
    conn = get_db_connection()
    if(request.method=="POST"):
        name = request.form['cert_name']
        description = request.form['cert_descr']
        level = request.form['cert_level']
        status = request.form['cert_status']
        training_status = request.form['cert_training_status']
        semester = request.form['cert_semester']
        year = request.form['cert_year']
        update_cert(conn, Cert_ID, name, level, description)
        update_cert_enrollment(conn, UIN, Cert_ID, status, training_status, semester, year)
        conn.close()
        if(is_admin()):
            return redirect(url_for('progress_bp.view_progress', UIN=UIN))
        return redirect(url_for('cert_bp.view_cert', UIN=UIN))
    cert = get_cert_enrollment(conn, UIN, Cert_ID)
    conn.close()
    return render_template('admin/update_cert_enrollment.html', UIN=UIN, cert=cert, is_admin=is_admin())

@cert_bp.route('/delete_cert_enrollment/<int:Cert_ID>/<int:UIN>', methods=['DELETE'])
@login_required
def delete_cert_enrollment(UIN, Cert_ID):
    conn = get_db_connection()
    delete_cert_enrollment(conn, UIN, Cert_ID)
    conn.close()
    return jsonify({"change": "program deleted"})



def is_admin():
    return current_user.user_type=="admin"

def get_all_certs(conn):
    return conn.execute('SELECT * FROM Certifications').fetchall()

def get_cert_enrollment(conn, UIN, Cert_ID):
    return conn.execute('SELECT * FROM View_CertEnrollmentDetails WHERE UIN=? AND Cert_ID=?', (UIN, Cert_ID)).fetchone()

# get certifications the current user is enrolled in
def get_user_enrolled_certs(conn, UIN):
    return conn.execute('SELECT * FROM View_CertEnrollmentDetails WHERE UIN=?', (UIN, )).fetchall()

# get certifications the current user is not enrolled in
def get_user_unenrolled_certs(conn, UIN):
    return conn.execute('SELECT * FROM Unenrolled_Certifications WHERE UIN=?', (UIN, )).fetchall()

# Create a Cert_Enrollment, extra values like status are added in update_cert_enrollment
def create_cert_enrollment(conn, UIN, Cert_ID):
    conn.execute('INSERT INTO Cert_Enrollment (UIN, Cert_ID) VALUES (?, ?)', (UIN, Cert_ID))
    conn.commit()

def update_cert(conn, Cert_ID, name, level, description):
    conn.execute('UPDATE Certification SET name=?, level=?, description=? WHERE Cert_ID=?', (name, level, description, Cert_ID))
    conn.commit()

# update cert enrollment
def update_cert_enrollment(conn, UIN, Cert_ID, status, training_status, semester, year):
    conn.execute('UPDATE Cert_Enrollment SET status=?, training_status=?, semester=?, year=? WHERE UIN=? AND Cert_ID=?', (status, training_status, semester, year, UIN, Cert_ID))
    conn.commit()

# delete cert enrollment by UIN and Cert_ID
def delete_cert_enrollment(conn, UIN, Cert_ID):
    conn.execute('DELETE FROM Cert_Enrollment WHERE UIN=? AND Cert_ID=?', (UIN, Cert_ID))
    conn.commit()


