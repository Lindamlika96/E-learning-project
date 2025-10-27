"""
POST /api/auth/signup
    ➤ Register a new user account

Request Body:
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
}

Response:
{
    "success": true,
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    },
    "message": "Account created successfully"
}

POST /api/auth/login
    ➤ Authenticate user and return user data

Request Body:
{
    "email": "john@example.com",
    "password": "securepassword123"
}

Response:
{
    "success": true,
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    },
    "message": "Login successful"
}
"""

from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models import User
import logging

log = logging.getLogger(__name__)

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user account."""
    data = request.get_json()
    
    # Validation
    if not data or not isinstance(data, dict):
        log.warning("Signup request body is missing or not JSON")
        return jsonify({"success": False, "error": "Invalid request body. JSON object expected."}), 400
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validate required fields
    if not name or len(name) < 2:
        return jsonify({"success": False, "error": "Name is required (minimum 2 characters)"}), 400
    
    if not email or '@' not in email or len(email) < 5:
        return jsonify({"success": False, "error": "Valid email address is required"}), 400
    
    if not password or len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters long"}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        log.warning(f"Signup attempt with existing email: {email}")
        return jsonify({"success": False, "error": "An account with this email already exists"}), 400
    
    try:
        # Hash the password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        log.info(f"New user registered: {email}")
        
        return jsonify({
            "success": True,
            "user": new_user.to_dict(),
            "message": "Account created successfully"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log.exception(f"Error during signup: {e}")
        return jsonify({"success": False, "error": "An error occurred during registration. Please try again."}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return user data."""
    data = request.get_json()
    
    # Validation
    if not data or not isinstance(data, dict):
        log.warning("Login request body is missing or not JSON")
        return jsonify({"success": False, "error": "Invalid request body. JSON object expected."}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validate required fields
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400
    
    try:
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            log.warning(f"Login attempt with non-existent email: {email}")
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        # Verify password
        if not bcrypt.check_password_hash(user.password_hash, password):
            log.warning(f"Failed login attempt for user: {email}")
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        log.info(f"User logged in successfully: {email}")
        
        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "message": "Login successful"
        }), 200
        
    except Exception as e:
        log.exception(f"Error during login: {e}")
        return jsonify({"success": False, "error": "An error occurred during login. Please try again."}), 500

