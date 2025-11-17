"""
Bot webhook client for sending notifications to the FastAPI bot engine.

Handles webhook delivery with retry logic and logging.
"""
import os
import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BotWebhookClient:
    """
    HTTP client for sending webhook notifications to the bot engine.
    
    Handles order status changes and admin reply notifications.
    """
    
    def __init__(self, bot_webhook_url: Optional[str] = None, bot_webhook_secret: Optional[str] = None):
        """
        Initialize the bot webhook client.
        
        Args:
            bot_webhook_url: URL of the bot webhook endpoint (defaults to env var)
            bot_webhook_secret: Shared secret for authentication (defaults to env var)
        """
        self.bot_webhook_url = (bot_webhook_url or os.getenv("BOT_WEBHOOK_URL", "")).rstrip('/')
        self.bot_webhook_secret = bot_webhook_secret or os.getenv("BOT_WEBHOOK_SECRET", "")
        
        if not self.bot_webhook_url:
            logger.warning("BOT_WEBHOOK_URL not configured - webhook notifications will be disabled")
        
        if not self.bot_webhook_secret:
            logger.warning("BOT_WEBHOOK_SECRET not configured - webhook authentication may fail")
        
        logger.info(f"BotWebhookClient initialized with URL: {self.bot_webhook_url}")
    
    def _send_webhook(
        self,
        payload: Dict[str, Any],
        max_retries: int = 3,
        timeout: int = 10
    ) -> bool:
        """
        Send webhook notification to bot with retry logic.
        Logs all attempts to the webhook_logs table.
        
        Args:
            payload: Webhook payload dictionary
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            
        Returns:
            True if webhook was delivered successfully, False otherwise
        """
        import json
        
        if not self.bot_webhook_url:
            logger.error("Cannot send webhook - BOT_WEBHOOK_URL not configured")
            self._log_webhook_attempt(
                event_type=payload.get("event", "unknown"),
                payload=payload,
                status_code=None,
                response="BOT_WEBHOOK_URL not configured",
                success=False
            )
            return False
        
        url = f"{self.bot_webhook_url}/webhook/backend"
        headers = {
            "X-Backend-Secret": self.bot_webhook_secret,
            "Content-Type": "application/json"
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Sending webhook to bot (attempt {attempt + 1}/{max_retries})",
                    extra={
                        "event": payload.get("event"),
                        "order_id": payload.get("order_id")
                    }
                )
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    logger.info(
                        "Webhook delivered successfully",
                        extra={
                            "event": payload.get("event"),
                            "order_id": payload.get("order_id"),
                            "status_code": response.status_code
                        }
                    )
                    self._log_webhook_attempt(
                        event_type=payload.get("event", "unknown"),
                        payload=payload,
                        status_code=response.status_code,
                        response=response.text[:500],  # Limit response length
                        success=True
                    )
                    return True
                else:
                    logger.warning(
                        f"Webhook delivery failed with status {response.status_code}",
                        extra={
                            "event": payload.get("event"),
                            "order_id": payload.get("order_id"),
                            "status_code": response.status_code,
                            "response": response.text
                        }
                    )
                    self._log_webhook_attempt(
                        event_type=payload.get("event", "unknown"),
                        payload=payload,
                        status_code=response.status_code,
                        response=response.text[:500],
                        success=False
                    )
            
            except requests.exceptions.Timeout:
                logger.warning(
                    f"Webhook request timed out (attempt {attempt + 1}/{max_retries})",
                    extra={
                        "event": payload.get("event"),
                        "order_id": payload.get("order_id")
                    }
                )
                if attempt == max_retries - 1:  # Log only on last attempt
                    self._log_webhook_attempt(
                        event_type=payload.get("event", "unknown"),
                        payload=payload,
                        status_code=None,
                        response=f"Timeout after {max_retries} attempts",
                        success=False
                    )
            
            except requests.exceptions.ConnectionError as e:
                logger.warning(
                    f"Webhook connection error (attempt {attempt + 1}/{max_retries}): {e}",
                    extra={
                        "event": payload.get("event"),
                        "order_id": payload.get("order_id")
                    }
                )
                if attempt == max_retries - 1:  # Log only on last attempt
                    self._log_webhook_attempt(
                        event_type=payload.get("event", "unknown"),
                        payload=payload,
                        status_code=None,
                        response=f"Connection error: {str(e)[:500]}",
                        success=False
                    )
            
            except Exception as e:
                logger.error(
                    f"Unexpected error sending webhook: {e}",
                    extra={
                        "event": payload.get("event"),
                        "order_id": payload.get("order_id")
                    },
                    exc_info=True
                )
                self._log_webhook_attempt(
                    event_type=payload.get("event", "unknown"),
                    payload=payload,
                    status_code=None,
                    response=f"Unexpected error: {str(e)[:500]}",
                    success=False
                )
                break  # Don't retry on unexpected errors
        
        logger.error(
            f"Failed to deliver webhook after {max_retries} attempts",
            extra={
                "event": payload.get("event"),
                "order_id": payload.get("order_id")
            }
        )
        return False
    
    def _log_webhook_attempt(
        self,
        event_type: str,
        payload: Dict[str, Any],
        status_code: Optional[int],
        response: str,
        success: bool
    ):
        """
        Log webhook delivery attempt to database.
        
        Args:
            event_type: Type of webhook event
            payload: Webhook payload
            status_code: HTTP status code (if available)
            response: Response text or error message
            success: Whether delivery was successful
        """
        try:
            import json
            from models import db, WebhookLog
            
            log_entry = WebhookLog(
                event_type=event_type,
                payload=json.dumps(payload),
                status_code=status_code,
                response=response,
                success=success
            )
            
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            # Don't fail webhook delivery if logging fails
            logger.error(f"Failed to log webhook attempt: {e}", exc_info=True)
    
    def notify_order_status_changed(
        self,
        order_id: str,
        status: str,
        telegram_id: str,
        chat_id: int,
        amount: Optional[float] = None,
        order_type: Optional[str] = None,
        admin_receipt: Optional[str] = None
    ) -> bool:
        """
        Notify bot of order status change.
        
        Args:
            order_id: Unique order identifier
            status: New order status (e.g., "approved", "declined", "completed")
            telegram_id: User's Telegram ID
            chat_id: User's chat ID
            amount: Order amount (optional)
            order_type: Order type - "buy" or "sell" (optional)
            admin_receipt: Admin confirmation receipt file ID (optional)
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        payload = {
            "event": "order_status_changed",
            "order_id": order_id,
            "status": status,
            "telegram_id": telegram_id,
            "chat_id": chat_id,
            "amount": amount,
            "order_type": order_type,
            "admin_receipt": admin_receipt
        }
        
        logger.info(
            f"Notifying bot of order status change: {order_id} -> {status}",
            extra={
                "order_id": order_id,
                "status": status,
                "telegram_id": telegram_id
            }
        )
        
        return self._send_webhook(payload)
    
    def notify_order_verified(
        self,
        order_id: str,
        telegram_id: str,
        chat_id: int,
        amount: float,
        order_type: str,
        price: float,
        user_bank: Optional[str] = None,
        receipt: Optional[str] = None
    ) -> bool:
        """
        Notify bot that admin verified an order.
        
        Args:
            order_id: Unique order identifier
            telegram_id: User's Telegram ID
            chat_id: User's chat ID
            amount: Order amount
            order_type: Order type - "buy" or "sell"
            price: Exchange rate/price
            user_bank: User's bank information (optional)
            receipt: Receipt file path (optional)
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        payload = {
            "event": "order_verified",
            "order_id": order_id,
            "telegram_id": telegram_id,
            "chat_id": chat_id,
            "amount": amount,
            "order_type": order_type,
            "price": price,
            "user_bank": user_bank,
            "receipt": receipt
        }
        
        logger.info(
            f"Notifying bot of order verification: {order_id}",
            extra={
                "order_id": order_id,
                "telegram_id": telegram_id,
                "order_type": order_type
            }
        )
        
        return self._send_webhook(payload)
    
    def notify_admin_replied(
        self,
        order_id: str,
        telegram_id: str,
        chat_id: int,
        message_content: Optional[str] = None,
        message_id: Optional[int] = None
    ) -> bool:
        """
        Notify bot that admin replied to an order.
        
        Args:
            order_id: Order identifier
            telegram_id: User's Telegram ID
            chat_id: User's chat ID
            message_content: Admin's message content (optional)
            message_id: Message ID in database (optional)
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        payload = {
            "event": "admin_replied",
            "order_id": order_id,
            "telegram_id": telegram_id,
            "chat_id": chat_id,
            "message_content": message_content,
            "message_id": message_id
        }
        
        logger.info(
            f"Notifying bot of admin reply for order: {order_id}",
            extra={
                "order_id": order_id,
                "telegram_id": telegram_id
            }
        )
        
        return self._send_webhook(payload)


# Global webhook client instance
_webhook_client: Optional[BotWebhookClient] = None


def get_webhook_client() -> BotWebhookClient:
    """
    Get the global webhook client instance.
    Creates the instance on first call.
    
    Returns:
        BotWebhookClient instance
    """
    global _webhook_client
    if _webhook_client is None:
        _webhook_client = BotWebhookClient()
    return _webhook_client
