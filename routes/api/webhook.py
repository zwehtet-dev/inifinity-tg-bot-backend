"""
Webhook API routes for bot notifications.

Internal endpoints for triggering webhook notifications to the bot engine.
"""
from flask import Blueprint, request, jsonify
import logging

from bot_webhook_client import get_webhook_client

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook_api', __name__, url_prefix='/api/webhook')


@webhook_bp.route('/notify-bot', methods=['POST'])
def notify_bot():
    """
    Internal endpoint to trigger webhook notification to bot.
    
    This endpoint is called internally by the backend when events occur
    that need to be communicated to the bot (e.g., order status changes).
    
    Request JSON:
        {
            "event": "order_status_changed" | "admin_replied",
            "order_id": str,
            "status": str (for order_status_changed),
            "telegram_id": str,
            "chat_id": int,
            "amount": float (optional),
            "order_type": str (optional),
            "admin_receipt": str (optional),
            "message_content": str (optional, for admin_replied),
            "message_id": int (optional, for admin_replied)
        }
    
    Returns:
        JSON response with status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        event = data.get("event")
        
        if not event:
            return jsonify({"error": "Event type is required"}), 400
        
        webhook_client = get_webhook_client()
        
        # Handle order status changed event
        if event == "order_status_changed":
            order_id = data.get("order_id")
            status = data.get("status")
            telegram_id = data.get("telegram_id")
            chat_id = data.get("chat_id")
            
            if not all([order_id, status, telegram_id, chat_id]):
                return jsonify({
                    "error": "Missing required fields: order_id, status, telegram_id, chat_id"
                }), 400
            
            success = webhook_client.notify_order_status_changed(
                order_id=order_id,
                status=status,
                telegram_id=telegram_id,
                chat_id=chat_id,
                amount=data.get("amount"),
                order_type=data.get("order_type"),
                admin_receipt=data.get("admin_receipt")
            )
            
            if success:
                return jsonify({"status": "ok", "message": "Webhook sent successfully"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to send webhook"}), 500
        
        # Handle admin replied event
        elif event == "admin_replied":
            order_id = data.get("order_id")
            telegram_id = data.get("telegram_id")
            chat_id = data.get("chat_id")
            
            if not all([order_id, telegram_id, chat_id]):
                return jsonify({
                    "error": "Missing required fields: order_id, telegram_id, chat_id"
                }), 400
            
            success = webhook_client.notify_admin_replied(
                order_id=order_id,
                telegram_id=telegram_id,
                chat_id=chat_id,
                message_content=data.get("message_content"),
                message_id=data.get("message_id")
            )
            
            if success:
                return jsonify({"status": "ok", "message": "Webhook sent successfully"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to send webhook"}), 500
        
        else:
            return jsonify({"error": f"Unknown event type: {event}"}), 400
    
    except Exception as e:
        logger.error(f"Error in notify-bot endpoint: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@webhook_bp.route('/test', methods=['POST'])
def test_webhook():
    """
    Test endpoint to verify webhook configuration.
    
    Sends a test webhook to the bot to verify connectivity.
    
    Returns:
        JSON response with test result
    """
    try:
        webhook_client = get_webhook_client()
        
        # Send a test notification
        test_payload = {
            "event": "order_status_changed",
            "order_id": "TEST-ORDER-123",
            "status": "test",
            "telegram_id": "123456789",
            "chat_id": 123456789,
            "amount": 100.0,
            "order_type": "buy"
        }
        
        success = webhook_client._send_webhook(test_payload)
        
        if success:
            return jsonify({
                "status": "ok",
                "message": "Test webhook sent successfully",
                "webhook_url": webhook_client.bot_webhook_url
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send test webhook",
                "webhook_url": webhook_client.bot_webhook_url
            }), 500
    
    except Exception as e:
        logger.error(f"Error in test webhook endpoint: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
