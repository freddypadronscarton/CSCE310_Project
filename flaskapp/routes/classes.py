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

def is_class_name_taken(conn, class_name):
  class_exist = conn.execute('SELECT COUNT(*) FROM Classes WHERE name=?', (class_name, )).fetchone()[0]
  if (class_exist > 0):
    return True
  else:
    return False

def add_new_class(conn, class_name, class_descr):
  conn.execute('INSERT INTO Classes (name, description) VALUES (?, ?)', (class_name, class_descr))
  conn.commit()

    

