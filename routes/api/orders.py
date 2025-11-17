from flask import Blueprint, jsonify, request
from models import db, User, Order, MyanmarBankAccount, TelegramID
from routes.api.auth import TOKEN_STORE
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from flask_sqlalchemy import SQLAlchemy
import uuid

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
    # Add detailed logging for debugging
    print("=" * 80)
    print("📥 BACKEND: Received order submission request")
    print("=" * 80)
    print(f"📋 Form data keys: {list(request.form.keys())}")
    print(f"📋 Form data: {dict(request.form)}")
    print(f"💰 Amount from form: '{request.form.get('amount')}' (type: {type(request.form.get('amount'))})")
    print(f"💵 Price from form: '{request.form.get('price')}' (type: {type(request.form.get('price'))})")
    print("=" * 80)
    
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
            print(f"❌ Missing required field: {field}")
            return jsonify({'error': f'{field} is required'}), 400

    # Convert numeric fields safely
    try:
        amount_str = data['amount']
        price_str = data['price']
        print(f"🔄 Converting amount: '{amount_str}' to float")
        print(f"🔄 Converting price: '{price_str}' to float")
        
        amount = float(amount_str)
        price = float(price_str)
        
        print(f"✅ Converted amount: {amount} (type: {type(amount)})")
        print(f"✅ Converted price: {price} (type: {type(price)})")
        
        if amount == 0.0:
            print(f"⚠️ WARNING: Amount is 0.0 after conversion!")
            
    except ValueError as e:
        print(f"❌ Conversion error: {e}")
        return jsonify({'error': 'Invalid amount or price format'}), 400

    # Handle uploaded receipt files (support multiple receipts)
    upload_dir = 'static/uploads/receipts'
    os.makedirs(upload_dir, exist_ok=True)
    receipt_paths = []
    qr_path = None

    # Iterate over all uploaded files
    for key in request.files:
        files = request.files.getlist(key)
        for file in files:
            if not file or not file.filename:
                continue
            
            # Generate secure filename
            ext = os.path.splitext(secure_filename(file.filename))[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            
            # Handle receipt files (support multiple)
            if key.startswith('receipt') or 'receipt' in key.lower():
                path = os.path.join(upload_dir, filename)
                file.save(path)
                receipt_paths.append(path)
            
            # Handle QR code file
            elif key == 'qr' or 'qr' in key.lower():
                qr_dir = 'static/uploads/qr'
                os.makedirs(qr_dir, exist_ok=True)
                qr_path = os.path.join(qr_dir, filename)
                file.save(qr_path)

    # Combine receipt paths as comma-separated string
    receipt_path = ",".join(receipt_paths) if receipt_paths else None
        
    # Handle Myanmar bank account - prioritize ID if provided, otherwise lookup by name
    myanmar_bank_id = None
    if data.get('myanmar_bank_account_id'):
        # Use the provided Myanmar bank account ID directly
        myanmar_bank_id = int(data.get('myanmar_bank_account_id'))
    elif data.get('myanmar_bank_account'):
        # Fallback: lookup by bank name
        mm_bank = data.get('myanmar_bank_account')
        mm_bank_account = MyanmarBankAccount.query.filter_by(bank_name=mm_bank).first()
        if mm_bank_account:
            myanmar_bank_id = mm_bank_account.id
        
    telegram_id = TelegramID.query.filter_by(chat_id=data.get('chat_id')).first()
    
    if not telegram_id:
        return jsonify({'error': 'Telegram ID not found for the provided chat_id'}), 404

    print(f"📝 Creating Order object with amount={amount}, price={price}")
    print(f"🏦 Bank IDs - Thai: {data.get('thai_bank_account_id')}, Myanmar: {myanmar_bank_id}")
    
    order = Order(
        order_type=data['order_type'],
        amount=amount,
        price=price,
        user_id=user.id if user else None,
        thai_bank_account_id=int(data.get('thai_bank_account_id')) if data.get('thai_bank_account_id') else None,
        myanmar_bank_account_id=myanmar_bank_id,
        receipt=receipt_path,
        confirm_receipt=data.get('confirm_receipt'),
        user_bank=data.get('user_bank'),
        telegram_id=telegram_id.id,
        qr=qr_path if qr_path else data.get('qr')
    )
    
    print(f"📝 Order object created, amount attribute: {order.amount}")
    
    order.order_id = generate_order_id(order.order_type)

    db.session.add(order)
    db.session.commit()
    
    print(f"💾 Order saved to database")
    print(f"💾 Order amount after commit: {order.amount}")
    print(f"✅ Order ID: {order.order_id}")
    print("=" * 80)

    return jsonify({
        'message': 'Order submitted successfully',
        'order_id': order.order_id,
        'order': {
            'id': order.id,
            'order_id': order.order_id,
            'order_type': order.order_type,
            'amount': order.amount,
            'price': order.price,
            'status': order.status,
            'receipt': order.receipt,
            'qr': order.qr,
            'user_bank': order.user_bank,
            'created_at': order.created_at.isoformat()
        }
    }), 201

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


@latest_order_bp.route('/latest-pending', methods=['GET'])
def latest_pending_order_by_chat_id():
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return jsonify({'error': 'chat_id is required'}), 400

    telegram = TelegramID.query.filter_by(chat_id=chat_id).first()
    if not telegram:
        return jsonify({'error': 'Telegram ID not found'}), 404

    latest_order = Order.query.filter_by(
        telegram_id=telegram.id
    ).order_by(Order.created_at.desc()).first()

    latest_pending_order = latest_order if latest_order and latest_order.status == 'pending' else None

    if not latest_pending_order:
        return jsonify({'has_pending': False, 'order': None})

    order_data = {
        'id': latest_pending_order.id,
        'order_id': latest_pending_order.order_id,
        'order_type': latest_pending_order.order_type,
        'amount': latest_pending_order.amount,
        'price': latest_pending_order.price,
        'created_at': latest_pending_order.created_at.isoformat(),
        'status': latest_pending_order.status,
        'thai_bank_account_id': latest_pending_order.thai_bank_account_id,
        'myanmar_bank_account_id': latest_pending_order.myanmar_bank_account_id,
        'receipt': latest_pending_order.receipt,
        'confirm_receipt': latest_pending_order.confirm_receipt,
        'user_bank': latest_pending_order.user_bank,
        'qr': latest_pending_order.qr
    }
    return jsonify({'has_pending': True, 'order': order_data})


@latest_order_bp.route('/<string:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    """Get order details by order_id."""
    order = Order.query.filter_by(order_id=order_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Get telegram info for chat_id
    telegram_info = None
    if order.telegram:
        telegram_info = {
            'id': order.telegram.id,
            'chat_id': order.telegram.chat_id,
            'telegram_id': order.telegram.telegram_id
        }
    
    order_data = {
        'id': order.id,
        'order_id': order.order_id,
        'order_type': order.order_type,
        'amount': order.amount,
        'price': order.price,
        'created_at': order.created_at.isoformat(),
        'status': order.status,
        'thai_bank_account_id': order.thai_bank_account_id,
        'myanmar_bank_account_id': order.myanmar_bank_account_id,
        'receipt': order.receipt,
        'confirm_receipt': order.confirm_receipt,
        'user_bank': order.user_bank,
        'qr': order.qr,
        'telegram': telegram_info
    }
    return jsonify(order_data)


@latest_order_bp.route('/<string:order_id>/confirm-receipt', methods=['POST'])
def upload_confirm_receipt(order_id):
    """Upload admin confirmation receipt for an order."""
    order = Order.query.filter_by(order_id=order_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if file is in request
    if 'receipt' not in request.files:
        return jsonify({'error': 'No receipt file provided'}), 400
    
    file = request.files['receipt']
    
    if not file or not file.filename:
        return jsonify({'error': 'Invalid file'}), 400
    
    # Save the file
    upload_dir = 'static/uploads/confirm_receipts'
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate secure filename
    ext = os.path.splitext(secure_filename(file.filename))[1]
    filename = f"{order_id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)
    
    file.save(filepath)
    
    # Update order with confirm_receipt path
    order.confirm_receipt = filepath
    db.session.commit()
    
    return jsonify({
        'message': 'Confirmation receipt uploaded successfully',
        'order_id': order_id,
        'confirm_receipt': filepath
    }), 200


@latest_order_bp.route('/<string:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    """Update order status."""
    order = Order.query.filter_by(order_id=order_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Get status from request body
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    new_status = data['status']
    
    # Validate status
    valid_statuses = ['pending', 'verified', 'approved', 'declined', 'complain']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
    
    # Update status
    old_status = order.status
    order.status = new_status
    db.session.commit()
    
    return jsonify({
        'message': 'Order status updated successfully',
        'order_id': order_id,
        'old_status': old_status,
        'new_status': new_status
    }), 200