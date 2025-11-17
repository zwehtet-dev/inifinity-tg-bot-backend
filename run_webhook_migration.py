"""
Script to run the webhook models migration.

This script creates the webhook_logs and bot_webhook_settings tables
in the database.

Usage:
    python run_webhook_migration.py
"""
from app import app, db
from models import WebhookLog, BotWebhookSettings
import os


def run_migration():
    """Create webhook-related tables in the database."""
    with app.app_context():
        # Check if tables already exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'webhook_logs' in existing_tables and 'bot_webhook_settings' in existing_tables:
            print("✓ Webhook tables already exist. No migration needed.")
            return
        
        print("Creating webhook tables...")
        
        # Create tables
        db.create_all()
        
        print("✓ Migration completed successfully!")
        print("  - Created 'webhook_logs' table")
        print("  - Created 'bot_webhook_settings' table")
        
        # Check if we need to insert default webhook settings
        settings_count = BotWebhookSettings.query.count()
        if settings_count == 0:
            bot_webhook_url = os.getenv('BOT_WEBHOOK_URL', '')
            bot_webhook_secret = os.getenv('BOT_WEBHOOK_SECRET', '')
            
            if bot_webhook_url and bot_webhook_secret:
                default_settings = BotWebhookSettings(
                    webhook_url=bot_webhook_url,
                    secret=bot_webhook_secret,
                    enabled=True
                )
                db.session.add(default_settings)
                db.session.commit()
                print(f"✓ Created default webhook settings with URL: {bot_webhook_url}")
            else:
                print("⚠ No default webhook settings created. Set BOT_WEBHOOK_URL and BOT_WEBHOOK_SECRET environment variables.")


if __name__ == '__main__':
    run_migration()
