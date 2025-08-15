from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bson import ObjectId
import base64
import os
from werkzeug.utils import secure_filename

def create_auth_routes(app, db, user_model, company_model, face_model):
    auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
    
    @auth_bp.route('/login', methods=['POST'])
    def login():
        """User login endpoint"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400
            
            # Authenticate user
            user = user_model.authenticate_user(username, password)
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Create access token
            access_token = create_access_token(identity=str(user['_id']))
            
            # Get company info if user has one
            company = None
            if user.get('company_id'):
                company = company_model.get_company_by_id(user['company_id'])
                company['_id'] = str(company['_id'])
            
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'role': user['role'],
                    'company': company,
                    'has_face_encoding': user.get('face_encoding') is not None
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @auth_bp.route('/register', methods=['POST'])
    def register():
        """User registration endpoint"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            role = data.get('role')
            company_id = data.get('company_id')
            face_image = data.get('face_image')  # Base64 encoded image
            
            if not username or not password or not role:
                return jsonify({'error': 'Username, password, and role are required'}), 400
            
            if role not in ['student', 'company_admin', 'faculty_admin']:
                return jsonify({'error': 'Invalid role'}), 400
            
            # For students and company admins, company_id is required
            if role in ['student', 'company_admin'] and not company_id:
                return jsonify({'error': 'Company ID is required for students and company admins'}), 400
            
            # Process face image if provided
            face_encoding = None
            if face_image:
                face_encoding, error = face_model.extract_face_encoding(face_image)
                if error:
                    return jsonify({'error': f'Face processing error: {error}'}), 400
            
            # Create user
            user_id, error = user_model.create_user(
                username=username,
                password=password,
                role=role,
                company_id=company_id,
                face_encoding=face_encoding
            )
            
            if error:
                return jsonify({'error': error}), 400
            
            return jsonify({
                'message': 'User registered successfully',
                'user_id': user_id
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @auth_bp.route('/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        """Get current user profile"""
        try:
            current_user_id = get_jwt_identity()
            user = user_model.get_user_by_id(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Get company info if user has one
            company = None
            if user.get('company_id'):
                company = company_model.get_company_by_id(user['company_id'])
                if company:
                    company['_id'] = str(company['_id'])
            
            return jsonify({
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'role': user['role'],
                    'company': company,
                    'has_face_encoding': user.get('face_encoding') is not None,
                    'created_at': user['created_at'].isoformat()
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @auth_bp.route('/update-face', methods=['POST'])
    @jwt_required()
    def update_face():
        """Update user's face encoding"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            face_image = data.get('face_image')
            
            if not face_image:
                return jsonify({'error': 'Face image is required'}), 400
            
            # Process face image
            face_encoding, error = face_model.extract_face_encoding(face_image)
            if error:
                return jsonify({'error': f'Face processing error: {error}'}), 400
            
            # Update user's face encoding
            result = user_model.update_face_encoding(current_user_id, face_encoding)
            
            if result.modified_count > 0:
                return jsonify({'message': 'Face encoding updated successfully'}), 200
            else:
                return jsonify({'error': 'Failed to update face encoding'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @auth_bp.route('/companies', methods=['GET'])
    @jwt_required()
    def get_companies():
        """Get all companies (for registration dropdown)"""
        try:
            companies = company_model.get_all_companies()
            
            # Convert ObjectId to string
            for company in companies:
                company['_id'] = str(company['_id'])
            
            return jsonify({'companies': companies}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @auth_bp.route('/create-company', methods=['POST'])
    @jwt_required()
    def create_company():
        """Create a new company (faculty admin only)"""
        try:
            current_user_id = get_jwt_identity()
            user = user_model.get_user_by_id(current_user_id)
            
            if not user or user['role'] != 'faculty_admin':
                return jsonify({'error': 'Only faculty admins can create companies'}), 403
            
            data = request.get_json()
            name = data.get('name')
            description = data.get('description', '')
            
            if not name:
                return jsonify({'error': 'Company name is required'}), 400
            
            company_id = company_model.create_company(name, description)
            
            return jsonify({
                'message': 'Company created successfully',
                'company_id': company_id
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return auth_bp