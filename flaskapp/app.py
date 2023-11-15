from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3


# App Initialization
app = Flask(__name__)
login_manager = LoginManager()
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager.init_app(app)


# Database Initialization
def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    
    # ITEMS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    description TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )''')
    # USERS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT)''')
    # COLLEGE STUDENTS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS college_students (
                    user_id INTEGER PRIMARY KEY,
                    UIN INTEGER,
                    GPA INTEGER,
                    major TEXT,
                    year INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )
                ''')
    # K12 STUDENTS TABLE
    conn.execute(''' CREATE TABLE IF NOT EXISTS k12_students (
                    user_id INTEGER PRIMARY KEY,
                    GPA INTEGER,
                    school TEXT,
                    grade INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )''')
    
    # SAMPLE INSERTS
    # conn.execute('''INSERT INTO k12_students (user_id, GPA, school, grade)
    #                     VALUES (1, 3.5, "Cinco Ranch High School", 11)''')

    # conn.execute('''INSERT INTO college_students (user_id, UIN, GPA, major, year)
    #                     VALUES (2, 10101, 4.0, "Computer Engineering", 2024)''')
    # conn.commit()

    # Sample Join for Specialization Hierarchy 
    example_join_query = '''
        SELECT users.user_id, users.username, users.password, 
               college_students.UIN, college_students.GPA, 
               college_students.major, college_students.year
        FROM users
        INNER JOIN college_students ON users.user_id = college_students.user_id
    '''
    
    column_names = ['user_id', 'username', 'password', 'UIN', 'GPA', 'major', 'year']
    college_students = conn.execute(example_join_query).fetchall()
    for row in college_students:
        row_str = ", ".join([f"{col_name}: {row[i]}" for i, col_name in enumerate(column_names)])
        print(row_str)

    print("Table created successfully")
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Flask-Login: User class and user_loader
class User(UserMixin):
    def __init__(self, id = None, username=None, password=None):
        if not id:
            self.id = id
        elif username is not None and password is not None:
            # Initialize with provided username and password
            self.id = id
            self.username = username
            self.password = password
        else:
            # Initialize by fetching from database
            conn = get_db_connection()
            query_result = conn.execute('SELECT * FROM users WHERE user_id = ?', (id,)).fetchone()
            conn.close()
            if query_result:
                self.id = id
                self.username = query_result["username"]
                self.password = query_result["password"]

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
        elif query_result["password"] == entered_password:
            # Create instance of the user class
            user = User(query_result["user_id"], entered_username, entered_password)
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

        
        if query_result:
            flash("That username is already in use. Please try again.", "Error")
        else:
            # CREATE: inserting new user into users table
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (entered_username, entered_password))
            conn.commit()
            flash("Successfully registered new user!", "Success")
            
        conn.close()  
     
    return render_template('register.html')



# HOME PAGE
@app.route('/home')
@login_required
def home():
    conn = get_db_connection()
    init_sqlite_db()
    items = conn.execute('SELECT * FROM items where user_id = ?', (current_user.id, )).fetchall()
    conn.close()
    return render_template('home.html', items=items)

# Sample CRUD operations (Create, Retreive, Update, Delete) 
# On the Home Page
@app.route('/item', methods=['POST'])
def add_item():
    print(current_user.id)
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


@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_sqlite_db()
    app.run(debug=True)
