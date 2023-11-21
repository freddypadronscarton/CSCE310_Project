from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

from db import *
from admin import admin_bp

# App Initialization
app = Flask(__name__)
login_manager = LoginManager()
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager.init_app(app)

#Blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')

# Flask-Login: User class and user_loader
class User(UserMixin):
    
    def __init__(self, id = None, username=None, email=None, f_name=None, l_name=None, is_admin=None, student_type=None):
        if username is not None:
            # Initialize with provided username and password
            self.id = id
            self.username = username
            self.email = email
            self.f_name = f_name
            self.l_name = l_name
            self.is_admin = is_admin
            self.student_type = student_type
        else:
            # Initialize by fetching from database
            conn = get_db_connection()
            query_result = conn.execute('SELECT * FROM users WHERE user_id = ?', (id,)).fetchone()
            conn.close()
            if query_result:
                self.id = id
                self.username = query_result["username"]
                self.email = query_result["email"]
                self.f_name = query_result["f_name"]
                self.l_name = query_result["l_name"]
                self.is_admin = query_result["is_admin"]
                self.student_type = query_result["student_type"]

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


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
        query_result = conn.execute('SELECT * FROM users where username = ?', (entered_username, )).fetchone()

        
        if not query_result:
            flash("That username is not registered. Please try again.", "Error")
        elif query_result["archived"]:
            flash("This account does not currently have access. Please contact administrators.")
        elif query_result["password"] == entered_password:
            # Create instance of the user class
            user = User(query_result["user_id"], query_result["email"], query_result["f_name"], query_result["l_name"], query_result["is_admin"], query_result['student_type'])
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
        entered_password = request.form['password']
        entered_confirmation = request.form['confirm']
        
        if not entered_confirmation == entered_password:
            flash("Passwords do not match. Please try again.", "Error")
            return render_template('register.html')
        
        # connect to db
        conn = get_db_connection()
        # query for users by entered username
        query_result = conn.execute('SELECT * FROM users where username = ?', (entered_username, )).fetchone()
        
        # TODO: Validate Email
        

        if query_result:
            flash("That username is already in use. Please try again.", "Error")
        else:
            register_user(conn, request, request.form['user_type'])
        conn.close()  
     
    return render_template('register.html')



# HOME PAGE
@app.route('/home')
@login_required
def home():
    conn = get_db_connection()

    if current_user.is_admin == "True":
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return render_template('home_admin.html', users=users)
    elif current_user.student_type == "college_student":
        items = conn.execute('SELECT * FROM items where user_id = ?', (current_user.id, )).fetchall()
        conn.close()
        return render_template('home_college.html', items=items)
    elif current_user.student_type == "k12_student":
        items = conn.execute('SELECT * FROM items where user_id = ?', (current_user.id, )).fetchall()
        conn.close()
        return render_template('home_k12.html', items=items)
    else:
        return render_template('login.html')
    
    
    
# Sample CRUD operations (Create, Retreive, Update, Delete) 
# On the Home Page
@app.route('/item', methods=['POST'])
def add_item():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('INSERT INTO items (user_id, name, description) VALUES (?, ?, ?)',
                 (current_user.id, data['name'], data['description']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'New item added'})

@app.route('/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items where user_id = ?', (current_user.id, )).fetchall()
    conn.close()
    return jsonify([{'name': item['name'], 'description': item['description']} for item in items])

@app.route('/item/<int:id>', methods=['PUT'])
def update_item(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE items SET description = ? WHERE id = ?',
                 (data['description'], id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item updated'})

@app.route('/item/<int:id>', methods=['DELETE'])
def delete_item(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item deleted'})

# helper function to print query results
def print_query_results(results, column_names):
    for row in results:
        row_str = ", ".join([f"{col_name}: {row[i]}" for i, col_name in enumerate(column_names)])
        print(row_str)


# Program Info Management Pages
@app.route('/program_application', method=['GET'])
def application(): 
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
    
@app.route('/program_application', method=['POST'])
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
    applied_programs = conn.execute('SELECT * FROM Programs WHERE Program_Num in (SELECT * FROM Application WHERE UIN = ?)', (current_user.id)).fetchall()
    conn.closes()
    return render_template('program_review.html', applied_programs=applied_programs)


@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_sqlite_db()
    app.run(debug=True)
