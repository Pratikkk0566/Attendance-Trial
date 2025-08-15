from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import gridfs
from bson import ObjectId
import pandas as pd
import io
import base64
import numpy as np
import face_recognition
import cv2
from PIL import Image
import json
from functools import wraps
from dotenv import load_dotenv

# Import our models and routes
from models import UserModel, CompanyModel, AttendanceModel, FaceRecognitionModel
from routes.auth import create_auth_routes
from routes.attendance import create_attendance_routes

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')  # Change this in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:3000'])  # Allow React frontend

# MongoDB Connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/attendance_app')
client = MongoClient(MONGODB_URI)
db = client.attendance_app
fs = gridfs.GridFS(db)

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize models
user_model = UserModel(db)
company_model = CompanyModel(db)
attendance_model = AttendanceModel(db)
face_model = FaceRecognitionModel()

# Register blueprints
auth_bp = create_auth_routes(app, db, user_model, company_model, face_model)
attendance_bp = create_attendance_routes(app, db, user_model, attendance_model, face_model)

app.register_blueprint(auth_bp)
app.register_blueprint(attendance_bp)

def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = user_model.get_user_by_id(current_user_id)
            if not user or user['role'] not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Database indexes for performance
def create_indexes():
    """Create database indexes for better performance"""
    try:
        # User indexes
        db.users.create_index('username', unique=True)
        db.users.create_index('role')
        db.users.create_index('company_id')
        
        # Attendance indexes
        db.attendance_records.create_index([('student_id', 1), ('timestamp', -1)])
        db.attendance_records.create_index('company_id')
        db.attendance_records.create_index('timestamp')
        db.attendance_records.create_index('status')
        
        # Company indexes
        db.companies.create_index('name')
        
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")

if __name__ == '__main__':
    # Create database indexes on startup
    create_indexes()
    app.run(debug=True, host='0.0.0.0', port=5000)