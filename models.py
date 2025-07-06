from flask_sqlalchemy import *
from datetime import datetime, timezone
import hashlib

db = SQLAlchemy()

class OTP(db.Model):
    __tablename__ = 'otp'
    
    id = db.Column(db.Integer, primary_key=True)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime, nullable=False)

    def is_valid(self):
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < expires_at

class MaintenanceMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    on = db.Column(db.Boolean, default=False)


class AuthFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    on = db.Column(db.Boolean, default=False)
   
class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    buy = db.Column(db.Float, nullable=False)
    sell = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed passwords
    created_at = db.Column(db.DateTime, default=datetime.now)

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
    user = db.relationship("User", backref="thai_bank_accounts")


class MyanmarBankAccount(db.Model):
    __tablename__ = 'myanmar_bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    on = db.Column(db.Boolean, default=True)
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    qr_image = db.Column(db.String(255), nullable=True)  # Path or URL to QR image
    user = db.relationship("User", backref="myanmar_bank_accounts")


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=True)  
    order_type = db.Column(db.Enum('buy', 'sell', name='order_type'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    thai_bank_account_id = db.Column(db.Integer, db.ForeignKey('thai_bank_accounts.id'), nullable=True)
    myanmar_bank_account_id = db.Column(db.Integer, db.ForeignKey('myanmar_bank_accounts.id'), nullable=True)
    receipt = db.Column(db.String(255), nullable=True)
    confirm_receipt = db.Column(db.String(255), nullable=True)  
    user_bank = db.Column(db.String(1024), nullable=True)  # User's bank account number
    qr = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('pending', 'approved', 'declined', name='order_status'), default='pending')

    thai_bank_account = db.relationship("ThaiBankAccount", backref="orders")
    myanmar_bank_account = db.relationship("MyanmarBankAccount", backref="orders")