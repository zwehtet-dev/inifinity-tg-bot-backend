from flask import Blueprint, request, jsonify
import hashlib
import secrets
import json
import os
from models import db, User  # Assuming `User` is your user model
from settings import SECRET_KEY  # Used to encode token securely
from datetime import datetime

# Create the Blueprint
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

# File path for storing tokens persistently
TOKEN_FILE = 'token_store.json'

# Helper function to load tokens from the JSON file


def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'w') as file:
            json.dump({}, file)
    with open(TOKEN_FILE, 'r') as file:
        return json.load(file)

# Helper function to save tokens to the JSON file


def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as file:
        json.dump(tokens, file)


# Load tokens at startup
TOKEN_STORE = load_tokens()


def generate_token(phone):
    """Generate a token using phone and a random secret."""
    random_string = secrets.token_hex(16)  # Generate a random string
    token = hashlib.sha256(
        f"{phone}{random_string}{SECRET_KEY}".encode()).hexdigest()
    return token


@auth_bp.route('/token', methods=['POST'])
def obtain_token():
    """View to obtain a token by posting phone and password."""
    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    # Check if phone and password are provided
    if not phone or not password:
        return jsonify({"error": "Phone and password are required"}), 400

    # Validate the user in the database
    user = User.query.filter_by(phone=phone).first()

    # Assuming passwords are hashed
    if not user or user.password != hashlib.sha256(password.encode()).hexdigest():
        return jsonify({"error": "Invalid phone or password"}), 401

    # Generate token
    token = generate_token(phone)

    # Store the token persistently
    TOKEN_STORE[token] = user.id
    save_tokens(TOKEN_STORE)

    # Return token and user info
    user_info = {
        "id": user.id,
        "phone": user.phone,
        "name": user.name,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return jsonify({"token": token, "user": user_info}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with name, phone, and password."""
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')

    if not name or not phone or not password:
        return jsonify({"error": "Name, phone, and password are required"}), 400

    existing_user = User.query.filter_by(phone=phone).first()
    if existing_user:
        return jsonify({"error": "User with this phone number already exists"}), 409

    new_user = User(
        name=name,
        phone=phone,
        created_at=datetime.now()
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    token = generate_token(phone)
    TOKEN_STORE[token] = new_user.id
    save_tokens(TOKEN_STORE)

    user_info = {
        "id": new_user.id,
        "phone": new_user.phone,
        "name": new_user.name,
        "created_at": new_user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return jsonify({"message": "User registered successfully", "token": token, "user": user_info}), 201


@auth_bp.route('/account', methods=['GET'])
def account():
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
        return jsonify({"error": "User not found"}), 404

    # Return user account information
    user_info = {
        "id": user.id,
        "phone": user.phone,
        "name": user.name,
        "smile_balance": user.smile_balance,
        "php_balance": user.php_balance,
        "password": "Passwords are hashed for security reasons",
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return jsonify(user_info), 200
