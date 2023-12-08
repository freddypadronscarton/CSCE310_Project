# admin.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from datetime import datetime
from db import *
from util.Users import *
from util.Programs import *
from util.Events import *

admin_bp = Blueprint('admin_bp', __name__)

# ENDPOINT FOR ARCHIVED BUTTON
@admin_bp.route('/archive_user/<int:UIN>', methods=['PUT'])
@login_required
def archive_user(UIN):
    data = request.get_json()
    # connect to db
    conn = get_db_connection()
    
    # Updates Archived field to provided value for given UIN
    update_user_field(conn, UIN, 'Archived', data['value'])
    
    # commit and close
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User archived'})


# ENDPOINT FOR DELETE BUTTON
@admin_bp.route('/delete_user/<int:UIN>', methods=['DELETE'])
@login_required
def delete_user_button(UIN):
    if int(current_user.__dict__['uin']) == int(UIN):
        logout_user()
     
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
    selected_user = get_user(conn, UIN)
    phone_str = str(selected_user["Phone"])
    if phone_str == "None":
        del selected_user['Phone']
    elif phone_str:
        selected_user['Phone'] = phone_str[:3] + "-" + phone_str[3:6] + "-" + phone_str[6:]
    
    
    return render_template('admin/changeUserTypeForm.html', selected_user= selected_user, user_type= user_type, current_year=datetime.now().year)

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

# ENDPOINT FOR FOR EDIT USER BUTTON
@admin_bp.route('/edit/user/<int:UIN>', methods=['GET', 'POST'])
@login_required
def editUser(UIN):
    
    conn = get_db_connection()

    # Perform Read from Users table to get all user fields
    user_info = get_user(conn, UIN)
    
    if request.method == 'POST':
        
        # Check if email and username are already taken
        if not request.form.get('Username') == user_info['Username'] and check_user_username(conn, request.form.get('Username')):
            flash("That username is already in use. Please try another.", "Error")
            return redirect(url_for('admin_bp.editUser', UIN=UIN))
        elif not request.form.get('Email') == user_info['Email'] and check_user_email(conn, request.form.get('Email')):
            flash("That email is already in use. Please try another.", "Error")
            return redirect(url_for('admin_bp.editUser', UIN=UIN))
        
        # Change any User Table fields
        user_info['Username'] = request.form.get('Username')
        user_info['First_Name'] = request.form.get('First_Name')
        user_info['M_Initial'] = request.form.get('M_Initial')
        user_info['Last_Name'] = request.form.get('Last_Name')
        user_info['Email'] = request.form.get('Email')
        user_info['Discord_Name'] = request.form.get('Discord_Name')
        
        # Fields for k12 and college
        if not user_info['User_Type'] == "admin":
            user_info['Gender'] = request.form.get("Gender")
            user_info['Hispanic_Or_Latino'] = 1 if "Hispanic_Or_Latino" in request.form else 0
            user_info['Race'] = request.form.get("Race")
            user_info['First_Generation'] = 1 if "First_Generation" in request.form else 0
            user_info['US_Citizen'] = 1 if "US_Citizen" in request.form else 0
            user_info['Birthdate'] = request.form.get("Birthdate")
            user_info['School'] = request.form.get('School')
            user_info['Classification'] = request.form.get('Classification')
            user_info['Phone'] = "".join(request.form.get('Phone').split("-"))

        # college student exclusive fields
        if user_info['User_Type'] == "college_student":
            user_info['GPA'] = request.form.get('GPA')
            user_info['Major'] = request.form.get('Major')
            user_info['Minor'] = request.form.get('Minor')
            user_info['Second_Minor'] = request.form.get('Second_Minor')
            user_info['Exp_Graduation'] = request.form.get('Exp_Graduation')
        
        update_user_fields(conn, user_info)
        conn.close()
        
        flash('Profile updated successfully.')
        return redirect(url_for('admin_bp.editUser', UIN=UIN))

    if not user_info["Phone"]:
        del user_info["Phone"]
    else:
        phone_str = str(user_info['Phone'])
        user_info['Phone'] = phone_str[:3] + "-" + phone_str[3:6] + "-" + phone_str[6:]
    
    # GET REQUEST JUST RENDERS TEMPLATE
    conn.close()
    return render_template('admin/edit_user.html', user=user_info, current_year=datetime.now().year)

# AUTHOR: Kelvin Zheng
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
            return redirect(url_for("home"))
    return render_template("admin/admin_add_program.html")
    
# AUTHOR: Kelvin Zheng
# ENDPOINT FOR ADMIN TO VIEW ALL PROGRAMS
@admin_bp.route('/view_programs', methods=['GET'])
@login_required
def view_all_programs():
    conn = get_db_connection()
    programs = get_all_programs(conn)
    conn.close()
    return render_template("admin/admin_view_programs.html", programs=programs)

# AUTHOR: Kelvin Zheng  
# ENDPOINT FOR ARCHIVING AND UNARCHIVING PROGRAMS
@admin_bp.route('/archive_program', methods=['PUT'])
@login_required
def archive_program():
    data = request.get_json()
    conn = get_db_connection()
    update_program_archive_status(conn, data["program_num"], data["archive"])
    conn.close()
    return jsonify({"user archive status": data["archive"]})

# AUTHOR: Kelvin Zheng
# ENDPOINT FOR DELETING A PROGRAM
@admin_bp.route('/delete_program/<int:program_num>', methods=['DELETE'])
@login_required
def delete_program(program_num):
    conn = get_db_connection()
    delete_program_backend(conn, program_num)
    conn.close()
    return jsonify({"change": "program deleted"})

# AUTHOR: Kelvin Zheng
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
    return render_template("admin/admin_update_program.html", program=program)

# AUTHOR: Kelvin Zheng
# ENDPOINT FOR GETTING A PROGRAM REPORT
@admin_bp.route('/get_report/<int:program_num>')
def get_report(program_num):
    conn = get_db_connection()
    
    program = get_program(conn, program_num)
    num_students = get_program_num_students(conn, program_num)

    # num that completed all opportunities
    completed_students_count = num_students_completed_program(conn, program_num)

    num_in_foreign_lang = num_in_program_and_coursetype(conn, program_num, 'foreign language')
    num_in_cryptogrpahy = num_in_program_and_coursetype(conn, program_num, 'cryptography')
    num_in_cryptogrpahy += num_in_program_and_coursetype(conn, program_num, 'cryptography mathematics')
    num_in_data_science = num_in_program_and_coursetype(conn, program_num, 'data science')

    minority_count = conn.execute("SELECT COUNT(*) FROM View_CollegeStudentDetails WHERE race != 'white'").fetchone()[0]
    # Error checking to prevent divide by zero errors
    if (num_students == 0):
        minority_percent = 0
    else:
        minority_percent = minority_count/num_students * 100
    if (minority_percent > 100):
      print("Error, impossible for minority percent to be over 100%")
      minority_percent = 100
    
    k12 = get_program_num_k12_students(conn, program_num)

    DoD_training_completed = num_w_specified_DoD_training_status(conn, program_num, "Complete")
    DoD_training_enrolled = num_w_specified_DoD_training_status(conn, program_num, "Enrolled")
    
    DoD_cert_complete = num_completed_DoD_cert(conn, program_num)
    fed_internships = num_federal_internships(conn, program_num)

    majors_data = get_prog_student_majors(conn, program_num)
    
    # converts majors_data into a dictionary w {major: student count} values
    majors_dict = {"None": 0}
    for major in majors_data:
        # Handle null values in database gracefully
        if (major[0] == None):
            majorName = "None"
        else:
          majorName = major[0]
        currCount = majors_dict.get(majorName, -1)
        if (currCount == -1):
            majors_dict.update({majorName: 1})
        else:
            majors_dict.update({majorName: currCount + 1})
            
    internship_list = []
    all_internship_names = names_of_prog_student_internships(conn, program_num)
    if all_internship_names != None:
      for internship in all_internship_names:
          internship_list.append(internship[0])
          

    program_report = {
        "name" : program["name"],
        "descr" : program["description"],
        "num_students": num_students,
        "completed_students_count": completed_students_count,
        "num_in_foreign_lang_courses": num_in_foreign_lang,
        "num_in_crypt_courses": num_in_cryptogrpahy,
        "num_in_data_science_courses": num_in_data_science,        
        "minority_participation": f"{minority_percent: .2f}%",
        "num_k12_accepted": k12,
        "DoD_training_enrolled": DoD_training_enrolled,
        "DoD_training_completed": DoD_training_completed,
        "DoD_cert_complete": DoD_cert_complete,
        "fed_internships" : fed_internships,
        "student_majors": majors_dict,
        "internship_names": internship_list
    }
    
    return render_template("admin/get_program_report.html", program=program_report)

# ENDPOINT FOR ADMIN TO VIEW ALL EVENTS - Christian Jeardoe
@admin_bp.route('/view_events', methods=['GET'])
@login_required
def view_all_events():
    conn = get_db_connection()
    events = get_all_events(conn)
    conn.close()
    return render_template("admin/admin_view_events.html", events=events)

# ENDPOINT FOR ADMIN TO ADD EVENTS - Christian Jeardoe
@admin_bp.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if (request.method == "POST"):
        Program_Num = request.form['program_num']
        UIN = current_user.id
        Start_Date = request.form['start_date']
        Time = request.form['time']
        Location = request.form['location']
        End_Date = request.form['end_date']
        Event_Type = request.form['event_type']
        conn = get_db_connection()
        add_new_event(conn, Program_Num, UIN, Start_Date, Time, Location, End_Date, Event_Type)
        conn.close()
        return render_template("admin/admin_home.html")
    return render_template("admin/admin_add_event.html")

# ENDPOINT FOR ADMIN TO DELETE EVENTS - Christian Jeardoe
@admin_bp.route('/delete_event/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    conn = get_db_connection()
    delete_event_backend(conn, event_id)
    conn.close()
    return jsonify({"success": "event deleted"})

# ENDPOINT FOR ADMIN UPDATE EVENTS - Christian Jeardoe
@admin_bp.route('/update_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    conn =  get_db_connection()
    if (request.method == 'POST'):
        update_event_info(conn, event_id, request.form["program_num"], request.form["UIN"], request.form["start_date"], request.form["time"], request.form["location"], request.form["end_date"], request.form["event_type"])
        conn.close()
        return redirect(url_for('admin_bp.view_all_events'))
    event = get_event(conn, event_id)
    conn.close()
    return render_template("update_event.html", event=event)

# ENDPOINT FOR ADMIN ATTENDEE CONTROL - Christian Jeardoe
@admin_bp.route('/attendee_control/<int:event_id>', methods=['GET', 'POST'])
@login_required
def attendee_control(event_id):
    conn = get_db_connection()
    event_attendance = get_students_by_event(conn, event_id)
    if (request.method == 'POST'):
        get_students_by_event(conn, event_id)
        conn.close()
        return render_template("admin/admin_attendee_control.html", event_attendance=event_attendance)
    conn.close()
    return render_template("admin/admin_attendee_control.html", event_attendance=event_attendance)

# ENDPOINT FOR ADMIN TO ADD ATTENDEES TO AN EVENT - Christian Jeardoe
@admin_bp.route('/add_attendee/<int:event_id>', methods=['GET', 'POST'])
@login_required
def add_attendee(event_id):
    conn = get_db_connection()
    if (request.method == 'POST'):
        add_student_to_event(conn, event_id, request.form["UIN"])
        conn.close()
        return redirect(url_for('admin_bp.attendee_control', event_id=event_id))
    event_attendance = get_event_attendance(conn, event_id)
    conn.close()
    return render_template("admin/admin_attendee_control.html", event_attendance=event_attendance)

# ENDPOINT FOR ADMIN TO REMOVE ATTENDEES FROM AN EVENT - Christian Jeardoe
@admin_bp.route('/delete_attendee/<int:event_id>/<int:UIN>', methods=['DELETE'])
@login_required
def delete_attendee(event_id, UIN):
    conn = get_db_connection()
    delete_attendee_backend(conn, event_id, UIN)
    conn.close()
    return jsonify({"success": "attendee deleted"})

