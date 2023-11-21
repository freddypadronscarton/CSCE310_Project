from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

from db import *
from util.Users import *
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
@app.route('/program_application', methods=['GET'])
def program_application(): 
    conn = get_db_connection()

    if current_user.is_admin == "True":
      # FIXME: ADD CORRECT MANAGER CODE LATER
      conn.close()
    else:
      programs = conn.execute('SELECT * FROM programs').fetchall()
      conn.close()
      return render_template('program_application', programs=programs)
  
@app.route('/program_application/<int:Program_Num>', methods=['GET']) # FIXME: MAKE PROGRAM NUM COME FROM FORM AND NOT THE URL??
def check_if_already_applied(program_num):
    conn = get_db_connection()
    alreadyApplied = conn.execute("SELECT COUNT(*) FROM Application WHERE Program_Num = ? AND UIN = ?", (program_num, current_user.id)).fetchone()
    conn.close()
    if (alreadyApplied > 0):
        flash("You've already applied to this program")
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
    # get next available application num
    app_num = conn.execute('SELECT MAX(App_Num) FROM Application').fetchone() + 1
    print(app_num) # debugging statement
    conn.execute('INSERT INTO Application (App_Num, Program_Num, UIN, Uncom_cert, Com_Cert, Purpose_statement) VALUES (?, ?, ?, ?, ?, ?)',
                 (app_num, program_num, current_user.id, uncom_cert, com_cert, purpose_statement))
    conn.commit()
    conn.close()
    return jsonify({"message": "application sent"})


@app.route('/program_review')
def get_applied_programs():
    conn = get_db_connection()
    applied_programs = conn.execute("""
                                    SELECT Programs.Program_Num, Programs.Name, Programs.Description, Applied.App_Num FROM Programs 
                                    INNER JOIN 
                                    (SELECT * FROM Application WHERE UIN = ?) AS Applied 
                                    ON Programs.Program_Num = Applied.Program_Num
                                    """,
                                     (current_user.id)).fetchall()
    accepted_programs = conn.execute('SELECT * FROM Track WHERE Student_Num = ?', (current_user.id)).fetchall()

    programs = []
    programs_status = []
    for program in applied_programs:
        programs.append(program)

      # looking to see if user has been accepted to the program yet
        program_found = False
        for accepted in accepted_programs:
            if (program[0] == accepted[0]):
                program_found = True
        
        if (program_found):
            programs_status.append(True)
        else:
            programs_status.append(False)
    
    applications = [{"program": p, "status": st} for p, st in zip(programs, programs_status)]
    
    conn.closes()
    return render_template('program_review.html', applications=applications)


@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_sqlite_db()
    app.run(debug=True)
