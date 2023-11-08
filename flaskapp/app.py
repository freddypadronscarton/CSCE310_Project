from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT)')
    print("Table created successfully")
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/item', methods=['POST'])
def add_item():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('INSERT INTO items (name, description) VALUES (?, ?)',
                 (data['name'], data['description']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'New item added'})

@app.route('/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
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
    conn.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item deleted'})


@app.route('/')
def home():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('home.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)
