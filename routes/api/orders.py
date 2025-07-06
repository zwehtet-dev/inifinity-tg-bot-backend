from flask import Blueprint, jsonify, request
from models import db, User, Order
from routes.api.auth import TOKEN_STORE
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from flask_sqlalchemy import SQLAlchemy

latest_order_bp = Blueprint('latest_order', __name__, url_prefix='/api/orders')

def generate_order_id(order_type):
    """
    Generates a unique order_id in the format DDMMYYA####B/S.
    
    - DDMMYY: current date
    - A: fixed prefix
    - ####: zero-padded increment ID per day
    - B or S: order type suffix (Buy/Sell)

    Args:
        order_type (str): 'buy' or 'sell'

    Returns:
        str: generated order_id
    """
    now = datetime.now()
    date_str = now.strftime("%d%m%y")  # 251225

    # Filter orders created today (between 00:00 and 23:59:59)
    start_of_day = datetime(now.year, now.month, now.day)
    end_of_day = start_of_day + timedelta(days=1)

    order_count_today = db.session.query(func.count(Order.id)).filter(
        and_(
            Order.created_at >= start_of_day,
            Order.created_at < end_of_day
        )
    ).scalar()

    increment = str(order_count_today + 1).zfill(4)  # e.g., 0001
    suffix = 'B' if order_type.lower() == 'buy' else 'S'

    return f"{date_str}A{increment}{suffix}"

@latest_order_bp.route('/submit', methods=['POST'])
def submit_order():
    token = request.headers.get('Authorization')
    user_id = None

    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
        user_id = TOKEN_STORE.get(token)

    user = User.query.get(user_id) if user_id else None

    # Use request.form for text fields
    data = request.form

    required_fields = ['order_type', 'amount', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Convert numeric fields safely
    try:
        amount = float(data['amount'])
        price = float(data['price'])
    except ValueError:
        return jsonify({'error': 'Invalid amount or price format'}), 400

    # Handle uploaded receipt file (optional)
    receipt_file = request.files.get('receipt')
    receipt_path = None

    if receipt_file:
        filename = secure_filename(receipt_file.filename)
        upload_dir = 'static/uploads/receipts'  # Create this folder in your project
        os.makedirs(upload_dir, exist_ok=True)
        receipt_path = os.path.join(upload_dir, filename)
        receipt_file.save(receipt_path)

    order = Order(
        order_type=data['order_type'],
        amount=amount,
        price=price,
        user_id=user.id if user else None,
        thai_bank_account_id=int(data.get('thai_bank_account_id')) if data.get('thai_bank_account_id') else None,
        myanmar_bank_account_id=int(data.get('myanmar_bank_account_id')) if data.get('myanmar_bank_account_id') else None,
        receipt=receipt_path,
        confirm_receipt=data.get('confirm_receipt'),
        user_bank=data.get('user_bank'),
        qr=data.get('qr')
    )
    
    order.order_id = generate_order_id(order.order_type)

    db.session.add(order)
    db.session.commit()

    return jsonify({'message': 'Order submitted successfully', 'order_id': order.order_id}), 201

@latest_order_bp.route('/latest_order', methods=['GET'])
def get_latest_order():
    """View to retrieve account information using a token."""
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    # Validate token
    user_id = TOKEN_STORE.get(token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    # Retrieve user from the database
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    latest_order = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).first()
    if not latest_order:
        return jsonify({'error': 'No orders found for this user'}), 404

    order_data = {
        'id': latest_order.id,
        'order_id': latest_order.order_id,  # Assuming order_id is a field in Order model
        'order_type': latest_order.order_type,
        'amount': latest_order.amount,
        'price': latest_order.price,
        'created_at': latest_order.created_at.isoformat(),
        'status': latest_order.status,
        'thai_bank_account_id': latest_order.thai_bank_account_id,
        'myanmar_bank_account_id': latest_order.myanmar_bank_account_id,
        'receipt': latest_order.receipt,
        'confirm_receipt': latest_order.confirm_receipt,
        'user_bank': latest_order.user_bank,
        'qr': latest_order.qr
    }
    return jsonify(order_data)