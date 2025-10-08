from flask_sqlalchemy import *
from datetime import datetime, timezone, timedelta

db = SQLAlchemy()

def now_mmt():
    return datetime.now(timezone.utc) + timedelta(hours=6, minutes=30)

class OTP(db.Model):
    __tablename__ = 'otp'
    
    id = db.Column(db.Integer, primary_key=True)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=now_mmt)
    expires_at = db.Column(db.DateTime, nullable=False)

    def is_valid(self):
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < expires_at

class MaintenanceMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    on = db.Column(db.Boolean, default=False)
    
    
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1024), nullable=False)
    chosen_option = db.Column(db.String(1024), nullable=True)
    image = db.Column(db.Text, nullable=True)
    from_bot = db.Column(db.Boolean, default=False)
    from_backend = db.Column(db.Boolean, default=False)
    seen_by_user = db.Column(db.Boolean, default=False)
    seen_by_admin = db.Column(db.Boolean, default=False)
    buttons = db.Column(db.String(1024), nullable=True)  # Store buttons as JSON string
    telegram_id = db.Column(db.String(255), db.ForeignKey('telegram_ids.telegram_id'), nullable=False)

class TelegramID(db.Model):
    __tablename__ = 'telegram_ids'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(255))
    telegram_id = db.Column(db.String(255), unique=True, nullable=True)
    user = db.relationship("Message", backref="telegram", lazy=True)
    orders = db.relationship("Order", backref="telegram", lazy=True)
    created_at = db.Column(db.DateTime, default=now_mmt)
    updated_at = db.Column(db.DateTime, default=now_mmt, onupdate=now_mmt)

    @property
    def last_order(self):
        return max(self.orders, key=lambda o: o.created_at) if self.orders else None

    @property
    def last_order_is_pending(self):
        last = self.last_order
        return last is not None and last.status == 'pending'


class AuthFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    on = db.Column(db.Boolean, default=False)
   
class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    buy = db.Column(db.Float, nullable=False)
    sell = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=now_mmt, onupdate=now_mmt)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed passwords
    created_at = db.Column(db.DateTime, default=now_mmt)
    
    sign_up_approved = db.Column(db.Boolean, default=False)

    # Relationship with Order
    orders = db.relationship("Order", backref="user", lazy=True, cascade="all, delete-orphan")
    def set_password(self, raw_password):
        import hashlib
        self.password = hashlib.sha256(raw_password.encode()).hexdigest()


class ThaiBankAccount(db.Model):
    __tablename__ = 'thai_bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    on = db.Column(db.Boolean, default=False)
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    qr_image = db.Column(db.String(255), nullable=True)  # Path or URL to QR image
    # user = db.relationship("User", backref="thai_bank_accounts")


class MyanmarBankAccount(db.Model):
    __tablename__ = 'myanmar_bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    on = db.Column(db.Boolean, default=True)
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    qr_image = db.Column(db.String(255), nullable=True)  # Path or URL to QR image
    # user = db.relationship("User", backref="myanmar_bank_accounts")


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer, db.ForeignKey('telegram_ids.id'), nullable=True)
    order_id = db.Column(db.String(50), unique=True, nullable=True)  
    order_type = db.Column(db.Enum('buy', 'sell', name='order_type'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    created_at = db.Column(db.DateTime, default=now_mmt)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    thai_bank_account_id = db.Column(db.Integer, db.ForeignKey('thai_bank_accounts.id'), nullable=True)
    myanmar_bank_account_id = db.Column(db.Integer, db.ForeignKey('myanmar_bank_accounts.id'), nullable=True)
    receipt = db.Column(db.Text, nullable=True)
    confirm_receipt = db.Column(db.Text, nullable=True)  
    user_bank = db.Column(db.String(1024), nullable=True)  # User's bank account number
    qr = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='pending')

    thai_bank_account = db.relationship("ThaiBankAccount", backref="orders")
    myanmar_bank_account = db.relationship("MyanmarBankAccount", backref="orders")