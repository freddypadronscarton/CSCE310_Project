# admin.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from db import *
from util.Users import *
from util.Programs import *

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
        
        # Change any User Table fields
        user_info['Username'] = request.form.get('username')
        user_info['First_Name'] = request.form.get('first_name')
        user_info['M_Initial'] = request.form.get('middle_initial')
        user_info['Last_Name'] = request.form.get('last_name')
        user_info['Email'] = request.form.get('email')
        user_info['Discord_Name'] = request.form.get('discord')
        
        # Change College Student Fields
        if user_info['User_Type'] == "college_student":
            user_info['Gender'] = request.form.get("gender")
            user_info['Hispanic_Or_Latino'] = 1 if "hispanic_or_latino" in request.form else 0
            user_info['Race'] = request.form.get("race")
            user_info['First_Generation'] = 1 if "first_gen" in request.form else 0
            user_info['US_Citizen'] = 1 if "US_citizen" in request.form else 0
            user_info['Birthdate'] = request.form.get("birthdate")
            
            user_info['GPA'] = request.form.get('gpa')
            user_info['Major'] = request.form.get('major')
            user_info['Minor'] = request.form.get('minor')
            user_info['Second_Minor'] = request.form.get('second_minor')
            user_info['Exp_Graduation'] = request.form.get('Exp_Graduation')
            user_info['Phone'] = "".join(request.form.get('phone_number').split("-"))
        
        user_info['School'] = request.form.get('school')
        user_info['Classification'] = request.form.get('classification')

        
        conn = get_db_connection()
        update_user_fields(conn, user_info)
        conn.close()
        
        flash('Profile updated successfully.')
        return redirect(url_for('admin_bp.editUser', UIN=UIN))
    else: # Get Request
        conn = get_db_connection()
        query_result = conn.execute('SELECT * FROM Users WHERE UIN = ?', (UIN,)).fetchone()
        
        if query_result:
            user_info['username'] = query_result["Username"]
            user_info['email'] = query_result["Email"]
            user_info['first_name'] = query_result["First_Name"]
            user_info['last_name'] = query_result["Last_Name"]
            user_info['user_type'] = query_result["User_Type"]
            user_info['middle_initial'] = query_result["M_Initial"]
            user_info['discord_name'] = query_result["Discord_Name"]
            
            # Fetch additional details based on user type
            if not user_info['user_type'] == 'admin':
                college_query = 'SELECT * FROM College_Students WHERE UIN = ?'
                college_info = conn.execute(college_query, (UIN,)).fetchone()
                
                # Assign additional attributes specific to college students
                user_info['gender'] = college_info["Gender"]
                user_info['hispanic_or_latino'] = college_info["Hispanic_Or_Latino"]
                user_info['race'] = college_info["Race"]
                user_info['first_gen'] = college_info["First_Generation"]
                user_info['us_citizen'] = college_info["US_Citizen"]
                user_info['birthdate'] = college_info["Birthdate"]
                
                user_info['gpa'] = college_info["GPA"]
                user_info['major'] = college_info["Major"]
                user_info['minor'] = college_info["Minor"]
                user_info['second_minor'] = college_info["Second_Minor"]
                user_info['exp_graduation'] = college_info["Exp_Graduation"]
                user_info['school'] = college_info["School"]
                user_info['classification'] = college_info["Classification"]
                phone_str = str(college_info["Phone"])
                user_info['phone_number'] = phone_str[:3] + "-" + phone_str[3:6] + "-" + phone_str[6:]

        conn.close()
        return render_template('admin/edit_user.html', user=user_info, current_year=datetime.now().year)

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
    
# ENDPOINT FOR ADMIN TO VIEW ALL PROGRAMS
@admin_bp.route('/view_programs', methods=['GET'])
@login_required
def view_all_programs():
    conn = get_db_connection()
    programs = get_all_programs(conn)
    conn.close()
    return render_template("admin/admin_view_programs.html", programs=programs)
  
# ENDPOINT FOR ARCHIVING AND UNARCHIVING PROGRAMS
@admin_bp.route('/archive_program', methods=['PUT'])
@login_required
def archive_program():
    data = request.get_json()
    conn = get_db_connection()
    update_program_archive_status(conn, data["program_num"], data["archive"])
    conn.close()
    return jsonify({"user archive status": data["archive"]})

# ENDPOINT FOR DELETING A PROGRAM
@admin_bp.route('/delete_program/<int:program_num>', methods=['DELETE'])
@login_required
def delete_program(program_num):
    conn = get_db_connection()
    delete_program_backend(conn, program_num)
    conn.close()
    return jsonify({"change": "program deleted"})

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
    # return render_template("admin_update_program.html", program=program)


# ENDPOINT FOR GETTING REPORT FOR A PROGRAM
@admin_bp.route('/get_report/<int:program_num>')
@login_required
def get_report(program_num):
    conn = get_db_connection()
    program = get_program(conn, program_num);
    num_students = get_program_num_students(conn, program_num)[0];

    # missing attributes

    minority_count = conn.execute("SELECT COUNT(*) FROM View_CollegeStudentDetails WHERE race != 'white'").fetchone()[0]
    # Error checking to prevent divide by zero errors
    if (num_students == 0):
        minority_percent = 0
    else:
        minority_percent = minority_count/num_students * 100
    if (minority_percent > 100):
      print("Error, impossible for minority percent to be over 100%")
      minority_percent = 100
    
    k12 = conn.execute(f'''SELECT COUNT(*) FROM 
                        (SELECT * FROM TRACK WHERE program={program_num}) AS Accepted_students
                        INNER JOIN
                        (SELECT * FROM College_students WHERE student_type='k12_student') AS K12_students
                        ON Accepted_students.student_num=K12_students.UIN''').fetchone()[0]

    majors_data = conn.execute(f'''SELECT View_CollegeStudentDetails.major FROM
                               (SELECT * FROM TRACK WHERE program={program_num}) AS Accepted_students
                               INNER JOIN
                               View_CollegeStudentDetails
                               ON Accepted_students.student_num=View_CollegeStudentDetails.UIN''').fetchall()
    
    # converts majors_data into a dictionary w {major: student count} values
    majors_dict = {"None": 0}
    for major in majors_data:
        majorName = major[0]
        currCount = majors_dict.get(majorName, -1)
        if (currCount == -1):
            majors_dict.update({majorName: 1})
        else:
            majors_dict.update({majorName: currCount + 1})
    
    program_report = {
        "name" : program["name"],
        "descr" : program["description"],
        "num_students": num_students,

        # missing attributes
        
        "minority_participation": f"{minority_percent: .2f}%",
        "num_k12_accepted": k12,

        # num pursuing federal internships

        "student_majors": majors_dict 
    }
    conn.close()
    return render_template("get_program_report.html", program=program_report)
