from flask import Blueprint, render_template, request, jsonify
from models import db, Message, TelegramID
from sqlalchemy import desc
from json import loads, dumps
from utils import login_required

messages_bp = Blueprint('messages_bp', __name__, url_prefix='/messages')

@messages_bp.route('/')
@login_required
def chat_list():
    # List all Telegram IDs that have messages, sorted by latest message on top
    telegrams = (
        TelegramID.query
        .join(Message)
        .order_by(desc(Message.id))
        .all()
    )
    return render_template('messages/list.html', telegrams=telegrams)

@messages_bp.route('/<telegram_id>')
@login_required
def chat_detail(telegram_id):
    telegram = TelegramID.query.filter_by(telegram_id=telegram_id).first_or_404()
    return render_template('messages/chat.html', telegram=telegram, loads=loads)


@messages_bp.route('/api/<telegram_id>/messages')
@login_required
def api_messages(telegram_id):
    telegram = TelegramID.query.filter_by(telegram_id=telegram_id).first_or_404()
    messages = Message.query.filter_by(telegram_id=telegram_id).order_by(Message.id.asc()).all()
    data = [
        {
            "id": m.id,
            "content": m.content,
            "chosen_option": m.chosen_option,
            "image": m.image,
            "from_bot": m.from_bot,
            "from_backend": m.from_backend,
            "seen_by_user": m.seen_by_user,
            "buttons": m.buttons,
        }
        for m in messages
    ]
    # Get latest order if exists
    latest_order = (
        telegram.orders and sorted(telegram.orders, key=lambda o: o.created_at, reverse=True)[0]
    )
    order_data = None
    if latest_order:
        order_data = {
            "id": latest_order.id,
            "order_id": latest_order.order_id,
            "status": latest_order.status,
            "amount": latest_order.amount,
            "created_at": latest_order.created_at.isoformat() if latest_order.created_at else None,
            # Add more fields as needed
        }
    return jsonify({
        "telegram_id": telegram.telegram_id,
        "messages": data,
        "latest_order": order_data
    })


@messages_bp.route('/<telegram_id>/order_status', methods=['POST'])
@login_required
def update_order_status(telegram_id):
    """
    Update the latest order status for a given telegram_id.
    Expects JSON: { "status": "pending" | "approved" | "declined" }
    """
    telegram = TelegramID.query.filter_by(telegram_id=telegram_id).first_or_404()
    latest_order = (
        telegram.orders and sorted(telegram.orders, key=lambda o: o.created_at, reverse=True)[0]
    )
    if not latest_order:
        return jsonify({"error": "No orders found for this user."}), 404

    data = request.get_json()
    status = data.get("status")
    if status not in ("pending", "approved", "declined", "complain"):
        return jsonify({"error": "Invalid status."}), 400

    latest_order.status = status
    db.session.commit()
    return jsonify({"success": True, "order_id": latest_order.order_id, "new_status": status})
3

@messages_bp.route('/api/list')
@login_required
def api_chat_list():
    # API endpoint to get chat list (for polling)
    telegrams = TelegramID.query.join(Message).order_by(desc(Message.id)).all()
    data = [
        {
            "telegram_id": t.telegram_id,
            "last_message": t.user[-1].content if t.user else "",
            "last_order_status": t.last_order.status if t.last_order else "",
            "updated_at": t.updated_at.isoformat() if t.updated_at else ""
        }
        for t in telegrams
    ]
    return jsonify(data)

@messages_bp.route('/api/chat/<telegram_id>')
@login_required
def api_chat_detail(telegram_id):
    # API endpoint to get chat details (for polling)
    telegram = TelegramID.query.filter_by(telegram_id=telegram_id).first_or_404()
    
    messages = (
        Message.query
        .filter_by(telegram_id=telegram_id)
        .order_by(Message.id.desc())
        .limit(50)  # Limit to last 50 messages
        .all()
    )
    
    messages = list(reversed(messages))
    data = [
        {
            "id": m.id,
            "content": m.content,
            "chosen_option": m.chosen_option,
            "image": m.image.replace('\\', '/') if m.image else None,
            "from_bot": m.from_bot,
            "buttons": m.buttons if m.buttons else None,
            "created_at": m.id,  # You can add timestamp if you add it to the model
            "seen_by_admin": m.seen_by_admin,
        }
        for m in messages
    ]
    
    # Mark all messages as seen by admin
    for m in messages:
        if not m.seen_by_admin:
            m.seen_by_admin = True
    db.session.commit()
    
    return jsonify({
        "telegram_id": telegram.telegram_id,
        "messages": data
    })