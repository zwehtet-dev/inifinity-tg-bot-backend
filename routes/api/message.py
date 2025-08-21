from flask import Blueprint, request, jsonify
from models import db, Message, TelegramID, User, Order
from routes.api.auth import TOKEN_STORE
import os
import uuid
from werkzeug.utils import secure_filename

message_bp = Blueprint('message_bp', __name__, url_prefix='/api/message')

@message_bp.route('/submit', methods=['POST'])
def submit_message():
    telegram_id = request.form.get('telegram_id')
    chat_id = request.form.get('chat_id')
    content = request.form.get('content')
    chosen_option = request.form.get('chosen_option')
    from_bot = request.form.get('from_bot', 'false').lower() == 'true'
    from_backend = request.form.get('from_backend', 'false').lower() == 'true'
    buttons = request.form.get('buttons', None)
    image_urls = []

    # Handle multiple image file uploads
    if 'image' in request.files:
        images = request.files.getlist('image')
        for image in images:
            filename = secure_filename(image.filename)
            image_path = os.path.join('static/uploads/images', str(uuid.uuid4()) + '_' + filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
            image_urls.append(image_path)

    if not telegram_id:
        return jsonify({"error": "telegram_id is required"}), 400

    # Ensure TelegramID exists or create it
    telegram_obj = TelegramID.query.filter_by(chat_id=chat_id).first()
    if not telegram_obj:
        telegram_obj = TelegramID(chat_id=chat_id, telegram_id=telegram_id)
        db.session.add(telegram_obj)
        db.session.commit()

    # Create the message
    image_url_str = ",".join(image_urls) if image_urls else None
    message = Message(
        content=content,
        chosen_option=chosen_option,
        image=image_url_str,
        telegram_id=telegram_obj.telegram_id,
        from_bot=from_bot,
        from_backend=from_backend,
        buttons=buttons if buttons else None,
        seen_by_admin=False
    )
    db.session.add(message)

    # If the message is from bot or backend and has images, update pending order's confirm_receipt
    if (from_bot or from_backend) and image_url_str:
        latest_order = Order.query.filter_by(
            telegram_id=telegram_obj.id,
        ).order_by(Order.created_at.desc()).first()
        if latest_order and content and content.strip() == 'confirmed':
            latest_order.confirm_receipt = '/' + image_url_str

    db.session.commit()

    return jsonify({"message": "Message submitted successfully"}), 201


@message_bp.route('/poll', methods=['GET'])
def poll_unseen_from_backend_messages():
    telegram_id = request.args.get('telegram_id')
    chat_id = request.args.get('chat_id')

    if not telegram_id or not chat_id:
        return jsonify({"error": "telegram_id and chat_id are required"}), 400

    telegram_obj = TelegramID.query.filter_by(chat_id=chat_id).first()
    if not telegram_obj:
        return jsonify({"messages": []}), 200

    unseen_messages = Message.query.filter_by(
        telegram_id=telegram_obj.telegram_id,
        from_backend=True,
        seen_by_user=False
    ).all()

    messages_list = []
    for msg in unseen_messages:
        messages_list.append({
            "id": msg.id,
            "content": msg.content,
            "chosen_option": msg.chosen_option,
            "image": msg.image,
            "from_bot": msg.from_bot,
            "from_backend": msg.from_backend,
            "buttons": msg.buttons
        })
        msg.seen_by_user = True  # Mark as seen

    db.session.commit()

    return jsonify({"messages": messages_list}), 200