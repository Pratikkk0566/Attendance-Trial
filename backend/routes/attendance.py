from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import base64
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid

def create_attendance_routes(app, db, user_model, attendance_model, face_model):
    attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')
    
    @attendance_bp.route('/mark', methods=['POST'])
    @jwt_required()
    def mark_attendance():
        """Mark attendance for current user"""
        try:
            current_user_id = get_jwt_identity()
            user = user_model.get_user_by_id(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user['role'] != 'student':
                return jsonify({'error': 'Only students can mark attendance'}), 403
            
            data = request.get_json()
            selfie_image = data.get('selfie_image')  # Base64 encoded
            location = data.get('location')  # {latitude: float, longitude: float}
            
            if not selfie_image:
                return jsonify({'error': 'Selfie image is required'}), 400
            
            if not location or not location.get('latitude') or not location.get('longitude'):
                return jsonify({'error': 'Location coordinates are required'}), 400
            
            # Extract face encoding from selfie
            selfie_encoding, error = face_model.extract_face_encoding(selfie_image)
            if error:
                return jsonify({'error': f'Face processing error: {error}'}), 400
            
            # Compare with stored face encoding
            stored_encoding = user.get('face_encoding')
            if not stored_encoding:
                return jsonify({'error': 'No registered face found. Please register your face first.'}), 400
            
            # Verify face match
            is_match = face_model.compare_faces(stored_encoding, selfie_encoding)
            
            if not is_match:
                # Still save the record but mark as rejected
                status = "Rejected"
            else:
                status = "Present"
            
            # Save selfie image
            image_filename = f"selfie_{current_user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpg"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            
            # Decode and save image
            if selfie_image.startswith('data:image'):
                selfie_image = selfie_image.split(',')[1]
            
            image_bytes = base64.b64decode(selfie_image)
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            # Mark attendance
            attendance_id, error = attendance_model.mark_attendance(
                student_id=current_user_id,
                company_id=user.get('company_id'),
                location=location,
                image_path=image_path,
                status=status
            )
            
            if error:
                # Clean up the saved image if attendance marking failed
                try:
                    os.remove(image_path)
                except:
                    pass
                return jsonify({'error': error}), 400
            
            return jsonify({
                'message': 'Attendance marked successfully',
                'attendance_id': attendance_id,
                'status': status,
                'face_match': is_match,
                'timestamp': datetime.utcnow().isoformat()
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @attendance_bp.route('/my-records', methods=['GET'])
    @jwt_required()
    def get_my_attendance():
        """Get attendance records for current user"""
        try:
            current_user_id = get_jwt_identity()
            user = user_model.get_user_by_id(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user['role'] != 'student':
                return jsonify({'error': 'Only students can view personal attendance'}), 403
            
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            skip = (page - 1) * per_page
            
            # Get attendance records
            records, total = attendance_model.get_student_attendance(
                student_id=current_user_id,
                skip=skip,
                limit=per_page
            )
            
            # Format records
            formatted_records = []
            for record in records:
                formatted_record = {
                    'id': str(record['_id']),
                    'timestamp': record['timestamp'].isoformat(),
                    'status': record['status'],
                    'location': record['location'],
                    'date': record['timestamp'].strftime('%Y-%m-%d'),
                    'time': record['timestamp'].strftime('%H:%M:%S')
                }
                formatted_records.append(formatted_record)
            
            return jsonify({
                'records': formatted_records,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @attendance_bp.route('/records', methods=['GET'])
    @jwt_required()
    def get_attendance_records():
        """Get attendance records (admin only)"""
        try:
            current_user_id = get_jwt_identity()
            user = user_model.get_user_by_id(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user['role'] not in ['company_admin', 'faculty_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 50))
            skip = (page - 1) * per_page
            
            # Build filters
            filters = {}
            
            # Date range filter
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            if date_from and date_to:
                try:
                    # Add time to make it inclusive
                    date_from = datetime.fromisoformat(date_from).replace(hour=0, minute=0, second=0)
                    date_to = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59)
                    filters['date_from'] = date_from.isoformat()
                    filters['date_to'] = date_to.isoformat()
                except:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
            # Company filter (company admins can only see their company)
            company_id = request.args.get('company_id')
            if user['role'] == 'company_admin':
                filters['company_id'] = str(user['company_id'])
            elif company_id:
                filters['company_id'] = company_id
            
            # Status filter
            status = request.args.get('status')
            if status:
                filters['status'] = status
            
            # Student name search (this requires joining with users collection)
            student_name = request.args.get('student_name')
            if student_name:
                # Find students matching the name
                student_query = {
                    'username': {'$regex': student_name, '$options': 'i'},
                    'role': 'student'
                }
                if user['role'] == 'company_admin':
                    student_query['company_id'] = user['company_id']
                
                matching_students = list(db.users.find(student_query, {'_id': 1}))
                student_ids = [str(s['_id']) for s in matching_students]
                
                if not student_ids:
                    # No matching students found
                    return jsonify({
                        'records': [],
                        'pagination': {
                            'current_page': page,
                            'per_page': per_page,
                            'total': 0,
                            'pages': 0
                        }
                    }), 200
                
                # Add student filter
                filters['student_ids'] = student_ids
            
            # Get attendance records
            records, total = attendance_model.get_attendance_records(
                filters=filters,
                skip=skip,
                limit=per_page
            )
            
            # Get student and company info for each record
            formatted_records = []
            for record in records:
                # Get student info
                student = user_model.get_user_by_id(record['student_id'])
                
                # Get company info
                company = None
                if record.get('company_id'):
                    company = db.companies.find_one({'_id': record['company_id']})
                
                formatted_record = {
                    'id': str(record['_id']),
                    'student': {
                        'id': str(student['_id']) if student else None,
                        'username': student['username'] if student else 'Unknown'
                    },
                    'company': {
                        'id': str(company['_id']) if company else None,
                        'name': company['name'] if company else 'Unknown'
                    } if company else None,
                    'timestamp': record['timestamp'].isoformat(),
                    'status': record['status'],
                    'location': record['location'],
                    'date': record['timestamp'].strftime('%Y-%m-%d'),
                    'time': record['timestamp'].strftime('%H:%M:%S')
                }
                formatted_records.append(formatted_record)
            
            return jsonify({
                'records': formatted_records,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @attendance_bp.route('/export', methods=['GET'])
    @jwt_required()
    def export_attendance():
        """Export attendance records to Excel"""
        try:
            current_user_id = get_jwt_identity()
            user = user_model.get_user_by_id(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user['role'] not in ['company_admin', 'faculty_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            # Build filters (same as get_attendance_records)
            filters = {}
            
            # Date range filter
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            if date_from and date_to:
                try:
                    date_from = datetime.fromisoformat(date_from).replace(hour=0, minute=0, second=0)
                    date_to = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59)
                    filters['date_from'] = date_from.isoformat()
                    filters['date_to'] = date_to.isoformat()
                except:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
            # Company filter
            company_id = request.args.get('company_id')
            if user['role'] == 'company_admin':
                filters['company_id'] = str(user['company_id'])
            elif company_id:
                filters['company_id'] = company_id
            
            # Status filter
            status = request.args.get('status')
            if status:
                filters['status'] = status
            
            # Get all records (no pagination for export)
            records, _ = attendance_model.get_attendance_records(
                filters=filters,
                skip=0,
                limit=10000  # Large limit for export
            )
            
            # Prepare data for Excel
            excel_data = []
            for record in records:
                # Get student info
                student = user_model.get_user_by_id(record['student_id'])
                
                # Get company info
                company = None
                if record.get('company_id'):
                    company = db.companies.find_one({'_id': record['company_id']})
                
                excel_data.append({
                    'Student Name': student['username'] if student else 'Unknown',
                    'Company': company['name'] if company else 'Unknown',
                    'Date': record['timestamp'].strftime('%Y-%m-%d'),
                    'Time': record['timestamp'].strftime('%H:%M:%S'),
                    'Status': record['status'],
                    'Latitude': record['location'].get('latitude', ''),
                    'Longitude': record['location'].get('longitude', '')
                })
            
            # Create DataFrame and export to Excel
            import pandas as pd
            import io
            
            df = pd.DataFrame(excel_data)
            
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Attendance Records', index=False)
            
            output.seek(0)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'attendance_report_{timestamp}.xlsx'
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @attendance_bp.route('/image/<attendance_id>', methods=['GET'])
    @jwt_required()
    def get_attendance_image():
        """Get attendance image (admin only)"""
        try:
            current_user_id = get_jwt_identity()
            user = user_model.get_user_by_id(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user['role'] not in ['company_admin', 'faculty_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            # Get attendance record
            attendance_record = attendance_model.collection.find_one({'_id': ObjectId(attendance_id)})
            
            if not attendance_record:
                return jsonify({'error': 'Attendance record not found'}), 404
            
            # Check if company admin can access this record
            if user['role'] == 'company_admin' and attendance_record.get('company_id') != user['company_id']:
                return jsonify({'error': 'Access denied'}), 403
            
            image_path = attendance_record.get('image_path')
            if not image_path or not os.path.exists(image_path):
                return jsonify({'error': 'Image not found'}), 404
            
            return send_file(image_path)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return attendance_bp