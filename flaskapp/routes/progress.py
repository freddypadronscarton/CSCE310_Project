# progress.py
import json
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from db import *
from util.Users import *
from util.Programs import *
from routes.classes import *
from routes.intern import *
from routes.cert import *

progress_bp = Blueprint('progress_bp', __name__)



@progress_bp.route('/view_progress/<int:UIN>', methods=['GET'])
@login_required
def view_progress(UIN):
    if current_user.user_type != "admin":
        return jsonify({"Erorr" : "Access Denied"})
    conn = get_db_connection()
    programs = get_all_programs_by_user(conn, UIN)
    classes = get_all_classes_by_user(conn, UIN)
    interns = get_all_interns_by_user(conn, UIN)
    certs = get_user_enrolled_certs(conn, UIN)
    name = conn.execute('SELECT First_Name FROM Users WHERE UIN=?', (UIN,)).fetchone()
    conn.close()

    return render_template("admin/admin_program_progress.html", programs=programs, classes=classes, interns=interns, certs=certs, name=name['First_Name'])



# Handles ACCEPT or REJECT
@progress_bp.route('/accept_user', methods=['PUT'])
@login_required
def accept_user_into_program():
    if current_user.user_type != "admin":
        return jsonify({"Erorr" : "Access Denied"})
    conn = get_db_connection()
    
    data = request.data.decode('utf-8')  # Decode byte data to string
    data_dict = json.loads(data)  # Convert JSON string to Python dictionary

    UIN = data_dict['uin']
    program_num = data_dict['program_id']
    is_accepted = data_dict['accepted']
    
    addTrackRecord(conn, UIN, program_num, is_accepted)
    conn.close()
    
    return "SUCCESS"


@progress_bp.route('/update_program_progress', methods=['PUT'])
def update_program_progress():
    if current_user.user_type != "admin":
        return jsonify({"Erorr" : "Access Denied"})
    conn = get_db_connection()
    
    data = request.data.decode('utf-8')  # Decode byte data to string
    data_dict = json.loads(data)  # Convert JSON string to Python dictionary

    UIN = data_dict['uin']
    program_num = data_dict['program_id']
    status = data_dict['status']
    
    updateTrackRecord(conn, UIN, program_num, status)
    conn.close()
    
    return "SUCCESS"
