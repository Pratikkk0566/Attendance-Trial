from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import face_recognition
import numpy as np
import cv2 # Added missing import for cv2

class UserModel:
    """User model for handling user operations"""
    
    def __init__(self, db):
        self.collection = db.users
    
    def create_user(self, username, password, role, company_id=None, face_encoding=None):
        """Create a new user"""
        # Check if user already exists
        if self.collection.find_one({'username': username}):
            return None, "User already exists"
        
        user_data = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'role': role,  # 'student', 'company_admin', 'faculty_admin'
            'company_id': ObjectId(company_id) if company_id else None,
            'face_encoding': face_encoding.tolist() if face_encoding is not None else None,
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id), None
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        user = self.collection.find_one({'username': username, 'is_active': True})
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def update_face_encoding(self, user_id, face_encoding):
        """Update user's face encoding"""
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'face_encoding': face_encoding.tolist()}}
        )

class CompanyModel:
    """Company model for handling company operations"""
    
    def __init__(self, db):
        self.collection = db.companies
    
    def create_company(self, name, description=""):
        """Create a new company"""
        company_data = {
            'name': name,
            'description': description,
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        result = self.collection.insert_one(company_data)
        return str(result.inserted_id)
    
    def get_company_by_id(self, company_id):
        """Get company by ID"""
        return self.collection.find_one({'_id': ObjectId(company_id)})
    
    def get_all_companies(self):
        """Get all active companies"""
        return list(self.collection.find({'is_active': True}))

class AttendanceModel:
    """Attendance model for handling attendance operations"""
    
    def __init__(self, db):
        self.collection = db.attendance_records
    
    def mark_attendance(self, student_id, company_id, location, image_path, status="Present"):
        """Mark attendance for a student"""
        # Check if already marked today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        existing_record = self.collection.find_one({
            'student_id': ObjectId(student_id),
            'timestamp': {'$gte': today_start, '$lte': today_end}
        })
        
        if existing_record:
            return None, "Attendance already marked for today"
        
        attendance_data = {
            'student_id': ObjectId(student_id),
            'company_id': ObjectId(company_id) if company_id else None,
            'timestamp': datetime.utcnow(),
            'location': {
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude')
            },
            'image_path': image_path,
            'status': status,
            'created_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(attendance_data)
        return str(result.inserted_id), None
    
    def get_attendance_records(self, filters=None, skip=0, limit=50):
        """Get attendance records with optional filters"""
        query = {}
        
        if filters:
            if filters.get('student_id'):
                query['student_id'] = ObjectId(filters['student_id'])
            if filters.get('company_id'):
                query['company_id'] = ObjectId(filters['company_id'])
            if filters.get('date_from') and filters.get('date_to'):
                query['timestamp'] = {
                    '$gte': datetime.fromisoformat(filters['date_from']),
                    '$lte': datetime.fromisoformat(filters['date_to'])
                }
            if filters.get('status'):
                query['status'] = filters['status']
        
        # Get total count
        total = self.collection.count_documents(query)
        
        # Get records with pagination
        records = list(self.collection.find(query)
                      .sort('timestamp', -1)
                      .skip(skip)
                      .limit(limit))
        
        return records, total
    
    def get_student_attendance(self, student_id, skip=0, limit=50):
        """Get attendance records for a specific student"""
        query = {'student_id': ObjectId(student_id)}
        
        total = self.collection.count_documents(query)
        records = list(self.collection.find(query)
                      .sort('timestamp', -1)
                      .skip(skip)
                      .limit(limit))
        
        return records, total

class FaceRecognitionModel:
    """Face recognition utilities"""
    
    @staticmethod
    def extract_face_encoding(image_data):
        """Extract face encoding from image data"""
        try:
            # Convert base64 to image
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            # Decode base64
            import base64
            image_bytes = base64.b64decode(image_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR to RGB (OpenCV uses BGR, face_recognition uses RGB)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_image)
            
            if len(face_encodings) > 0:
                return face_encodings[0], None
            else:
                return None, "No face detected in image"
                
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    @staticmethod
    def compare_faces(known_encoding, unknown_encoding, tolerance=0.6):
        """Compare two face encodings"""
        if known_encoding is None or unknown_encoding is None:
            return False
        
        try:
            # Convert lists back to numpy arrays if needed
            if isinstance(known_encoding, list):
                known_encoding = np.array(known_encoding)
            if isinstance(unknown_encoding, list):
                unknown_encoding = np.array(unknown_encoding)
            
            # Compare faces
            results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=tolerance)
            return results[0] if results else False
            
        except Exception as e:
            print(f"Error comparing faces: {str(e)}")
            return False