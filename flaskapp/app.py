from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

from db import *
from util.Users import *
from util.Programs import *
from routes.admin import admin_bp
from routes.example import items_bp

# App Initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

#Blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(items_bp, url_prefix='/items')

# Flask-Login: User class and user_loader
class User(UserMixin):
    
    def __init__(self, UIN = None, Username=None, Email=None, First_Name=None, Last_Name=None, User_Type=None):
        self.id = UIN
        if Username is not None:
            # Initialize with provided username and password
            self.uin = UIN
            self.username = Username
            self.email = Email
            self.first_name = First_Name
            self.last_name = Last_Name
            self.user_type = User_Type
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

@login_manager.user_loader
def load_user(UIN):
    return User(UIN)


# LOGIN PAGE
@app.route('/', methods=['GET', 'POST'])
def login():    
    #handling the submission
    if request.method == 'POST':
        # fields from the submitted form
        entered_username = request.form['username']
        entered_password = request.form['password']
        
        # connect to db
        conn = get_db_connection()
        # query for users by entered username
        query_result = conn.execute('SELECT * FROM users where Username = ?', (entered_username, )).fetchone()

        
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
     
    return render_template('login.html')


# REGISTRATION PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():    
    #handling the submission
    #handling the submission
    
    if request.method == 'POST':
        # fields from the submitted form
        entered_username = request.form['username']
        entered_uin = request.form['uin']
        entered_password = request.form['password']
        entered_confirmation = request.form['confirm']
        
        if not entered_confirmation == entered_password:
            flash("Passwords do not match. Please try again.", "Error")
            return render_template('register.html')
        
        # connect to db
        conn = get_db_connection()
        # query for users by entered username
        check_username = conn.execute('SELECT * FROM Users where username = ?', (entered_username, )).fetchone()
        check_UIN = conn.execute('SELECT * FROM Users where UIN = ?', (entered_uin, )).fetchone()
        
        # TODO: Validate Email
        

        if check_username or check_UIN:
            flash("That username or UIN is already in use. Please try another.", "Error")
        else:
            register_user(conn, request.form)
            conn.commit()
            
        conn.close()  
     
    return render_template('register.html', current_year=datetime.now().year)


# HOME PAGE
@app.route('/home')
@login_required
def home():
    conn = get_db_connection()

    if current_user.user_type == "admin":
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return render_template('admin_home.html', users=users)
    elif current_user.user_type == "college_student":
        items = conn.execute('SELECT * FROM items where UIN = ?', (current_user.uin, )).fetchall()
        conn.close()
        return render_template('college_home.html', items=items)
    elif current_user.user_type == "k12_student":
        items = conn.execute('SELECT * FROM items where UIN = ?', (current_user.uin, )).fetchall()
        conn.close()
        return render_template('k12_home.html', items=items)
    else:
        return render_template('login.html')

# PROFILE PAGE



# Program Info Management Pages
@app.route('/program_application')
def program_application(): 
    conn = get_db_connection()
    programs = conn.execute('SELECT * FROM programs').fetchall()
    conn.close()
    return render_template('program_application.html', programs=programs)

# This is the endpoint for checking if a user has already applied to the program
@app.route('/program_applied_check/<int:program_num>')
def check_if_already_applied(program_num):
    conn = get_db_connection()
    alreadyApplied = conn.execute("SELECT COUNT(*) FROM Application WHERE Program_Num = ? AND UIN = ?", (program_num, current_user.uin)).fetchone()[0]
    conn.close()
    print(alreadyApplied)
    if (alreadyApplied > 0):
        return jsonify({'alreadyApplied': True})
    else:
        return jsonify({'alreadyApplied': False})
    
@app.route('/program_application', methods=['POST'])
def add_new_application():
    program_num = request.form['program_num']
    uncom_cert = request.form['uncom_cert']
    com_cert = request.form['com_cert']
    purpose_statement = request.form['purpose_statement']
    conn = get_db_connection()
    conn.execute('INSERT INTO Application (program_num, UIN, uncom_cert, com_cert, purpose_statement) VALUES (?, ?, ?, ?, ?)',
                (program_num, current_user.uin, uncom_cert, com_cert, purpose_statement))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))


@app.route('/program_review')
def application_review():
    conn = get_db_connection()

    # applied_programs = conn.execute('''SELECT Applied.app_num, Applied.program_num, Programs.name, Programs.description, Applied.uncom_cert, Applied.com_cert, Applied.purpose_statement, Accepted.tracking_num
    #                   FROM (SELECT * FROM Application WHERE UIN=?) AS Applied
    #                   LEFT OUTER JOIN
    #                   (SELECT * FROM Track WHERE student_num=?) AS Accepted
    #                   ON Applied.program_num = Accepted.program
    #                   JOIN Programs
    #                   ON Applied.program_num = Programs.program_num'''
    #                , (current_user.uin, current_user.uin)).fetchall()
    applied_programs = get_applied_programs(conn, current_user.uin)
    conn.close()

    return render_template('program_review.html', applied_programs=applied_programs)
    
@app.route('/update_program_app/<int:app_num>')
def load_update_appl_page(app_num):
    conn = get_db_connection()
    app = conn.execute("SELECT * FROM Application WHERE APP_NUM = ?", (app_num, )).fetchone()
    conn.close();
    return render_template("update_program_app.html", app=app)

@app.route('/update_application', methods=['POST'])
def update_application():
    app_num = request.form["app_num"]
    uncom_cert = request.form["uncom_cert"]
    com_cert = request.form["com_cert"]
    purpose_statement = request.form["purpose_statement"]
    conn = get_db_connection()
    conn.execute("UPDATE Application SET uncom_cert=?, com_cert=?, purpose_statement=? WHERE app_num=?"
                 , (uncom_cert, com_cert, purpose_statement, app_num))
    conn.commit()
    conn.close()
    return redirect(url_for('application_review'))

@app.route('/delete_application/<int:app_num>', methods=['DELETE'])
def delete_application(app_num):
  print("calling function")
  conn = get_db_connection()
  conn.execute(f"DELETE FROM Application WHERE app_num = {app_num}")
  conn.commit()
  conn.close()
  return jsonify({"success": "program application deleted"})
    
@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_sqlite_db()
    app.run(debug=True)
