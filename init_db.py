#!/usr/bin/env python3
"""Initialize database tables and create default records."""
from app import app, db
from models import MaintenanceMode, AuthFeature, ExchangeRate, BotWebhookSettings
from settings import BOT_WEBHOOK_URL, BOT_WEBHOOK_SECRET

def init_database():
    """Create all database tables and initialize default records."""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Initialize MaintenanceMode if not exists
        if not MaintenanceMode.query.first():
            maintenance = MaintenanceMode(on=False)
            db.session.add(maintenance)
            print("✓ MaintenanceMode initialized (off)")
        
        # Initialize AuthFeature if not exists
        if not AuthFeature.query.first():
            auth_feature = AuthFeature(on=False)
            db.session.add(auth_feature)
            print("✓ AuthFeature initialized (off)")
        
        # Initialize ExchangeRate if not exists
        if not ExchangeRate.query.first():
            exchange_rate = ExchangeRate(buy=1.0, sell=1.0)
            db.session.add(exchange_rate)
            print("✓ ExchangeRate initialized")
        
        # Initialize BotWebhookSettings if not exists and webhook URL is provided
        if not BotWebhookSettings.query.first() and BOT_WEBHOOK_URL:
            webhook_settings = BotWebhookSettings(
                webhook_url=BOT_WEBHOOK_URL,
                secret=BOT_WEBHOOK_SECRET or "default-secret",
                enabled=True
            )
            db.session.add(webhook_settings)
            print("✓ BotWebhookSettings initialized")
        
        # Commit all changes
        db.session.commit()
        print("✓ Database initialization complete")

if __name__ == "__main__":
    init_database()
