#!/usr/bin/env python3
"""
Database setup script for the Attendance App
This script creates initial companies and admin users for testing
"""

import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Setup initial database with sample data"""
    
    # Connect to MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/attendance_app')
    client = MongoClient(MONGODB_URI)
    db = client.attendance_app
    
    print("Setting up database...")
    
    # Create companies
    companies_data = [
        {
            'name': 'Tech Corp',
            'description': 'Technology company',
            'created_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'name': 'Business Solutions Ltd',
            'description': 'Business consulting company',
            'created_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'name': 'Innovation Hub',
            'description': 'Startup incubator',
            'created_at': datetime.utcnow(),
            'is_active': True
        }
    ]
    
    # Insert companies if they don't exist
    companies = []
    for company_data in companies_data:
        existing_company = db.companies.find_one({'name': company_data['name']})
        if not existing_company:
            result = db.companies.insert_one(company_data)
            companies.append(result.inserted_id)
            print(f"Created company: {company_data['name']}")
        else:
            companies.append(existing_company['_id'])
            print(f"Company already exists: {company_data['name']}")
    
    # Create initial users
    users_data = [
        {
            'username': 'faculty_admin',
            'password_hash': generate_password_hash('admin123'),
            'role': 'faculty_admin',
            'company_id': None,
            'face_encoding': None,
            'created_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'username': 'tech_admin',
            'password_hash': generate_password_hash('admin123'),
            'role': 'company_admin',
            'company_id': companies[0],  # Tech Corp
            'face_encoding': None,
            'created_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'username': 'business_admin',
            'password_hash': generate_password_hash('admin123'),
            'role': 'company_admin',
            'company_id': companies[1],  # Business Solutions Ltd
            'face_encoding': None,
            'created_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'username': 'john_student',
            'password_hash': generate_password_hash('student123'),
            'role': 'student',
            'company_id': companies[0],  # Tech Corp
            'face_encoding': None,
            'created_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'username': 'jane_student',
            'password_hash': generate_password_hash('student123'),
            'role': 'student',
            'company_id': companies[1],  # Business Solutions Ltd
            'face_encoding': None,
            'created_at': datetime.utcnow(),
            'is_active': True
        }
    ]
    
    # Insert users if they don't exist
    for user_data in users_data:
        existing_user = db.users.find_one({'username': user_data['username']})
        if not existing_user:
            db.users.insert_one(user_data)
            print(f"Created user: {user_data['username']} ({user_data['role']})")
        else:
            print(f"User already exists: {user_data['username']}")
    
    # Create indexes
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
        print(f"Note: Some indexes may already exist - {e}")
    
    print("\nDatabase setup completed!")
    print("\nDefault login credentials:")
    print("Faculty Admin: faculty_admin / admin123")
    print("Tech Corp Admin: tech_admin / admin123")
    print("Business Admin: business_admin / admin123")
    print("Student (Tech Corp): john_student / student123")
    print("Student (Business): jane_student / student123")
    print("\nNote: Students need to register their faces before marking attendance.")

if __name__ == '__main__':
    setup_database()