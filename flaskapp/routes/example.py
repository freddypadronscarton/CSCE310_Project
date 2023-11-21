from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from db import *
from util.Users import *

items_bp = Blueprint('items_bp', __name__)

# Sample CRUD operations (Create, Retreive, Update, Delete) 
# On the Home Page

@items_bp.route('/add', methods=['POST'])
def add_item():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('INSERT INTO items (UIN, name, description) VALUES (?, ?, ?)',
                 (current_user.uin, data['name'], data['description']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'New item added'})

@items_bp.route('/', methods=['GET'])
def get_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items where UIN = ?', (current_user.uin, )).fetchall()
    conn.close()
    return jsonify([{'name': item['name'], 'description': item['description']} for item in items])

@items_bp.route('/update/<int:id>', methods=['PUT'])
def update_item(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE items SET description = ? WHERE item_id = ?',
                 (data['description'], id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item updated'})

@items_bp.route('/<int:id>', methods=['DELETE'])
def delete_item(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE item_id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item deleted'})