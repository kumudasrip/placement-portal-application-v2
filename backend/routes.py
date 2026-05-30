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

    @app.route('/api/register/company', methods=['POST'])
    def register_company():
        data = request.json
        if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
            return jsonify({'msg': 'Username or email already exists'}), 400
        user = User(username=data['username'], email=data['email'], role='company')
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        company = Company(user_id=user.id, name=data.get('name', data['username']), hr_contact=data.get('hr_contact'), website=data.get('website'), industry=data.get('industry'), location=data.get('location'))
        db.session.add(company)
        db.session.commit()
        return jsonify({'msg': 'Company registered, pending admin approval'})

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'msg': 'Invalid credentials'}), 401
        if not user.is_active or user.is_blacklisted:
            return jsonify({'msg': 'Account is inactive or blacklisted'}), 403
        if user.role == 'company' and (not user.company or user.company.approval_status != 'approved'):
            return jsonify({'msg': 'Company not approved yet'}), 403
        access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
        return jsonify({'access_token': access_token, 'role': user.role, 'user_id': user.id})

    @app.route('/api/admin/summary', methods=['GET'])
    @jwt_required()
    def admin_summary():
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        return jsonify({
            'students': Student.query.count(),
            'companies': Company.query.count(),
            'drives': PlacementDrive.query.count(),
            'applications': Application.query.count()
        })

    @app.route('/api/admin/companies', methods=['GET'])
    @jwt_required()
    @cache.cached(timeout=300, query_string=True)
    def admin_list_companies():
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        search = request.args.get('search', '')
        query = Company.query
        if search:
            query = query.filter((Company.name.ilike(f'%{search}%')) | (Company.industry.ilike(f'%{search}%')))
        companies = query.all()
        return jsonify([{'id': c.id, 'name': c.name, 'status': c.approval_status, 'is_active': c.is_active, 'is_blacklisted': c.user.is_blacklisted, 'industry': c.industry} for c in companies])

    @app.route('/api/admin/companies/<int:company_id>/approve', methods=['POST'])
    @jwt_required()
    def admin_approve_company(company_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.get_or_404(company_id)
        if company.approval_status != 'pending':
            return jsonify({'msg': f'Company already {company.approval_status}. Cannot approve.'}), 400
        company.approval_status = 'approved'
        db.session.commit()
        cache.clear()
        send_enhanced_mail(
            company.user.email,
            'Company Approved',
            'company_approved',
            company_name=company.name
        )
        return jsonify({'msg': 'Company approved'})

    @app.route('/api/admin/companies/<int:company_id>/reject', methods=['POST'])
    @jwt_required()
    def admin_reject_company(company_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.get_or_404(company_id)
        if company.approval_status != 'pending':
            return jsonify({'msg': f'Company already {company.approval_status}. Cannot reject.'}), 400
        company.approval_status = 'rejected'
        db.session.commit()
        cache.clear()
        send_mail(company.user.email, 'Company Rejected', 'Your company registration was rejected.')
        return jsonify({'msg': 'Company rejected'})

    @app.route('/api/admin/companies/<int:company_id>/blacklist', methods=['POST'])
    @jwt_required()
    def admin_blacklist_company(company_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.get_or_404(company_id)
        company.is_active = False
        company.user.is_blacklisted = True
        db.session.commit()
        cache.clear()
        return jsonify({'msg': 'Company blacklisted'})
