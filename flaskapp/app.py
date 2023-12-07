from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import sqlite3
import os


from db import *
from util.Users import *
from util.Programs import *
from routes.admin import admin_bp
from routes.example import items_bp
from util.Documents import *
from routes.progress import progress_bp
from routes.classes import *
from routes.intern import *
from routes.document import *
from routes.cert import *
from routes.application import *


# App Initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Uploads Directory for documents
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#Blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(items_bp, url_prefix='/items')
app.register_blueprint(progress_bp, url_prefix='/progress')
app.register_blueprint(classes_bp, url_prefix='/classes')
app.register_blueprint(intern_bp, url_prefix='/internship')
app.register_blueprint(document_bp, url_prefix='/doc')
app.register_blueprint(cert_bp, url_prefix='/cert')
app.register_blueprint(application_bp, url_prefix='/app')

# Flask-Login: User class and user_loader
class User(UserMixin):
    
    def __init__(self, UIN = None, Username=None, Email=None, First_Name=None, Last_Name=None, User_Type=None, Middle_Initial=None, Discord_Name=None):
        self.id = UIN
        if Username is not None:
            # Initialize with provided username and password
            self.uin = UIN
            self.username = Username
            self.email = Email
            self.first_name = First_Name
            self.last_name = Last_Name
            self.user_type = User_Type
            self.middle_initial = Middle_Initial
            self.discord_name = Discord_Name
        else:
            # Initialize by fetching from database
            conn = get_db_connection()
            query_result = conn.execute('SELECT * FROM Users WHERE UIN = ?', (UIN,)).fetchone()
            conn.close()
            if query_result:
                self.uin = UIN
                self.username = query_result["Username"]
                self.email = query_result["Email"]
                self.first_name = query_result["First_Name"]
                self.last_name = query_result["Last_Name"]
                self.user_type = query_result["User_Type"]
                self.middle_initial = query_result["M_Initial"]
                self.discord_name = query_result["Discord_Name"]

@login_manager.user_loader
def load_user(UIN):
    return User(UIN)


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    #handling the submission
    if request.method == 'POST':
        # fields from the submitted form
        entered_username = request.form['username']
        entered_password = request.form['password']
        
        # connect to db
        conn = get_db_connection()
        # query for users by entered username
        query_result = conn.execute('SELECT * FROM Users where Username = ?', (entered_username, )).fetchone()

        
        if not query_result:
            flash("That username is not registered. Please try again.", "Error")
        elif query_result["Archived"]:
            flash("This account does not currently have access. Please contact administrators.")
        elif query_result["Password"] == entered_password:
            # Create instance of the user class
            user = User(query_result["UIN"], query_result["Email"], query_result["First_Name"], query_result["Last_Name"], query_result["User_Type"])
            # Log in the user
            login_user(user)
            conn.close()
            return redirect(url_for('home'))
        else:
            flash("Incorrect Password. Please try again.", "Error")
        conn.close()  
     
    if current_user.is_authenticated:
        return redirect(url_for('home'))
     
    return render_template('auth/login.html')


# REGISTRATION PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():    
    #handling the submission
    #handling the submission
    
    previous_entry = None
    
    if request.method == 'POST':
        # fields from the submitted form
        entered_username = request.form['username']
        entered_uin = request.form['uin']
        entered_password = request.form['password']
        entered_confirmation = request.form['confirm']
        entered_email = request.form['email']
        
        # save previous entry
        previous_entry = request.form
        
        
        # connect to db
        conn = get_db_connection()        
        
        if not entered_confirmation == entered_password:
            flash("Passwords do not match. Please try again.", "Error")
        elif check_user_username(conn,entered_username):
            flash("That username is already in use. Please try another.", "Error")
        elif check_user_email(conn, entered_email):
            flash("That email is already in use. Please try another.", "Error")
        elif check_user_uin(conn, entered_uin):
            flash("That UIN is already in use. Please try another.", "Error")
        else:
            register_user(conn, request.form)
            previous_entry = None
            
        conn.commit()   
        conn.close()  
     
    return render_template('auth/register.html', current_year=datetime.now().year, previous = previous_entry)


# HOME PAGE
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    conn = get_db_connection()

    if current_user.user_type == "admin":
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return render_template('admin/admin_home.html', users=users)
    elif current_user.user_type == "college_student":
        items = conn.execute('SELECT * FROM items where UIN = ?', (current_user.uin, )).fetchall()
        conn.close()
        return render_template('student/college_home.html', items=items)
    elif current_user.user_type == "k12_student":
        items = conn.execute('SELECT * FROM items where UIN = ?', (current_user.uin, )).fetchall()
        conn.close()
        return render_template('student/k12_home.html', items=items)
    else:
        conn.close()
        return render_template('auth/login.html')

# PROFILE PAGE
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # current UIN
    UIN = current_user.uin
    
    conn = get_db_connection()

    # Perform Read from Users table to get all user fields
    user_info = get_user(conn, UIN)
    
    if request.method == 'POST':
        
        # Check if email and username are already taken
        if not request.form.get('Username') == user_info['Username'] and check_user_username(conn, request.form.get('Username')):
            flash("That username is already in use. Please try another.", "Error")
            return redirect(url_for('profile'))
        elif not request.form.get('Email') == user_info['Email'] and check_user_email(conn, request.form.get('Email')):
            flash("That email is already in use. Please try another.", "Error")
            return redirect(url_for('profile'))
        
        
        # Change any User Table fields
        user_info['Username'] = request.form.get('Username')
        user_info['First_Name'] = request.form.get('First_Name')
        user_info['M_Initial'] = request.form.get('M_Initial')
        user_info['Last_Name'] = request.form.get('Last_Name')
        user_info['Email'] = request.form.get('Email')
        user_info['Discord_Name'] = request.form.get('Discord_Name')
        
        # Fields for k12 and college
        if not user_info['User_Type'] == "admin":
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
        return redirect(url_for('profile'))
    
    if not user_info["Phone"]:
        del user_info["Phone"]
    else:
        phone_str = str(user_info['Phone'])
        user_info['Phone'] = phone_str[:3] + "-" + phone_str[3:6] + "-" + phone_str[6:]
    
    # GET REQUEST JUST RENDERS TEMPLATE
    conn.close()
    return render_template('auth/Profile.html', user=user_info, current_year=datetime.now().year)

# PROFILE PAGE
@app.route('/passwordRecovery', methods=['GET', 'POST'])
def passwordRecovery():
    
    # saves previous entry of form (in case of failure)
    stored = {}
    
    if request.method == 'POST':
        # FORM FIELDS
        UIN = request.form.get("UIN")
        oldPassword = request.form.get("Old")
        newPassword = request.form.get("New")
        confirmation = request.form.get("Confirm")
        
        # save entry
        stored = {
            'UIN': UIN,
            'Old': oldPassword,
            'New': newPassword,
            'Confirm': confirmation
        }
        
        
        
        # Connect to database
        conn = get_db_connection()
        #Retrieve User info (for entered UIN)
        user_info = get_user(conn, UIN)
        
        if not user_info:
            flash("Invalid UIN entry.", UIN)
        elif not user_info["Password"] == oldPassword:
            flash("Incorrect old password entered.")
        elif not newPassword == confirmation:
            flash("Entered passwords do not match.")
        else:
            update_user_field(conn,UIN, 'Password', newPassword)
            conn.commit()
            flash("Password updated!")

        conn.close()
        
    
        
    return render_template('auth/PasswordRecovery.html', stored = stored)
        
  
@app.route("/logout", methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/class_enrollment/<int:UIN>', methods=['GET', 'POST'])
@login_required
def class_enrollment(UIN):
    if(request.method == "POST"):
        class_name = request.form['class_name']
        class_descr = request.form['class_descr']
        class_type = request.form['class_type']
        class_semester = request.form['class_semester']
        class_year = request.form['class_year']
        class_status = request.form['class_status']
        conn = get_db_connection()
        class_exist = get_class_by_name(conn, class_name)
        if class_exist:
            is_enrolled = get_enrollment(conn, class_exist['Class_ID'], UIN)
            if(is_enrolled):
                flash("You are already enrolled in this class")
            conn.close()
        else:
            enroll_class(conn, class_name, class_descr, class_type, class_semester, class_year, class_status, UIN)
            conn.close()
            return redirect(url_for("home"))
    return render_template('student/class_enrollment.html')


def is_admin():
    return current_user.User_Type == "admin"


if __name__ == '__main__':
    init_sqlite_db()
    
    #insert_mock_data()
    
    #store uploaded documents
    if not os.path.exists('uploads'):
        os.mkdir('uploads')
    app.run(debug=True)
