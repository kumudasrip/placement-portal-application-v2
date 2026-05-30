from flask import request, jsonify, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import os, csv
from io import StringIO, BytesIO
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app, db, jwt, mail, cache, celery):
    from models import User, Company, Student, PlacementDrive, Application
    from flask_mail import Message

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return identity
    
    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({'msg': 'Unprocessable entity', 'error': str(e)}), 422
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({'msg': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'msg': 'Invalid token', 'error': str(error)}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'msg': 'Missing authorization token'}), 401

    def get_role():
        claims = get_jwt()
        return claims.get('role')
    
    def get_user_id():
        return int(get_jwt_identity())

    @app.route('/api/register/student', methods=['POST'])
    def register_student():
        data = request.json
        if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
            return jsonify({'msg': 'Username or email already exists'}), 400
        user = User(username=data['username'], email=data['email'], role='student')
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        student = Student(
            user_id=user.id,
            name=data.get('name', data['username']),
            phone_number=data.get('phone_number'),
            college_name=data.get('college_name'),
            degree=data.get('degree'),
            department=data.get('department'),
            cgpa=data.get('cgpa'),
            year=data.get('year'),
            location=data.get('location')
        )
        db.session.add(student)
        db.session.commit()
        return jsonify({'msg': 'Student registered successfully'})