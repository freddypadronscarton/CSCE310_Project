# admin.py
from flask import Blueprint, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from db import get_db_connection

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/update_user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    conn = get_db_connection()
    data = request.get_json()

    query = f"UPDATE users SET {data['field']} = ? WHERE user_id = ?"
    conn.execute(query, (data['value'], user_id))
    
    conn.commit()
    conn.close()
    print("Updated User")
    return jsonify({'message': 'User archived'})


@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    # Logic to delete user
    print("Deleted User")
    return jsonify({'message': 'User deleted'})
