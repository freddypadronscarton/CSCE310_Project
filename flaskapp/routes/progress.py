# progress.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from db import *
from util.Users import *
from util.Programs import *

progress_bp = Blueprint('progress_bp', __name__)



@progress_bp.route('/view_progress/<int:UIN>', methods=['GET'])
@login_required
def view_progress(UIN):
    if current_user.user_type != "admin":
        return jsonify({"Erorr" : "Access Denied"})
    conn = get_db_connection()
    programs = conn.execute('SELECT * FROM View_ApplicationDetails where UIN = ?', (UIN,)).fetchall()
    # name = conn.execute('SELECT * FROM WHERE UIN = ?', (UIN,)).fetchone()
    conn.close()



    return render_template("admin/admin_program_progress.html", programs=programs)