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

    @app.route('/api/admin/companies/<int:company_id>/unblacklist', methods=['POST'])
    @jwt_required()
    def admin_unblacklist_company(company_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.get_or_404(company_id)
        company.is_active = True
        company.user.is_blacklisted = False
        db.session.commit()
        cache.clear()
        return jsonify({'msg': 'Company unblacklisted'})

    @app.route('/api/admin/students', methods=['GET'])
    @jwt_required()
    @cache.cached(timeout=300, query_string=True)
    def admin_list_students():
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        search = request.args.get('search', '')
        query = Student.query
        if search:
            query = query.filter((Student.name.ilike(f'%{search}%')) | (Student.department.ilike(f'%{search}%')) | (Student.user.has(User.email.ilike(f'%{search}%'))))
        students = query.all()
        return jsonify([{'id': s.id, 'name': s.name, 'department': s.department, 'is_active': s.is_active, 'is_blacklisted': s.user.is_blacklisted, 'email': s.user.email} for s in students])

    @app.route('/api/admin/students/<int:student_id>/blacklist', methods=['POST'])
    @jwt_required()
    def admin_blacklist_student(student_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.get_or_404(student_id)
        student.is_active = False
        student.is_blacklisted = True
        student.user.is_blacklisted = True
        db.session.commit()
        cache.clear()
        return jsonify({'msg': 'Student blacklisted'})

    @app.route('/api/admin/students/<int:student_id>/unblacklist', methods=['POST'])
    @jwt_required()
    def admin_unblacklist_student(student_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.get_or_404(student_id)
        student.is_active = True
        student.is_blacklisted = False
        student.user.is_blacklisted = False
        db.session.commit()
        cache.clear()
        return jsonify({'msg': 'Student unblacklisted'})

    @app.route('/api/admin/students/<int:student_id>', methods=['GET'])
    @jwt_required()
    def admin_get_student_detail(student_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.get_or_404(student_id)
        user = User.query.get(student.user_id)
        applications = Application.query.filter_by(student_id=student.id).all()
        
        return jsonify({
            'id': student.id,
            'name': student.name,
            'email': user.email,
            'phone_number': student.phone_number,
            'college_name': student.college_name,
            'degree': student.degree,
            'department': student.department,
            'cgpa': student.cgpa,
            'year': student.year,
            'location': student.location,
            'skills': student.skills,
            'education': student.education,
            'experience': student.experience,
            'resume': student.resume,
            'is_active': student.is_active,
            'is_blacklisted': student.is_blacklisted,
            'created_at': student.created_at.strftime('%Y-%m-%d'),
            'applications_count': len(applications),
            'applications': [
                {
                    'id': a.id,
                    'drive': a.drive.job_title,
                    'company': a.drive.company.name,
                    'status': a.status,
                    'date': a.application_date.strftime('%Y-%m-%d')
                } for a in applications
            ]
        })

    @app.route('/api/admin/students/<int:student_id>/download_resume', methods=['GET'])
    @jwt_required()
    def admin_download_student_resume(student_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.get_or_404(student_id)
        if not student.resume:
            return jsonify({'msg': 'Resume not found'}), 404
        resume_path = os.path.join(UPLOAD_FOLDER, student.resume)
        if not os.path.exists(resume_path):
            return jsonify({'msg': 'Resume file not found'}), 404
        return send_file(resume_path, as_attachment=True)

    @app.route('/api/admin/companies/<int:company_id>', methods=['GET'])
    @jwt_required()
    def admin_get_company_detail(company_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.get_or_404(company_id)
        user = User.query.get(company.user_id)
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        
        drives_data = []
        for drive in drives:
            total_applicants = Application.query.filter_by(drive_id=drive.id).count()
            drives_data.append({
                'id': drive.id,
                'job_title': drive.job_title,
                'status': drive.status,
                'applicants': total_applicants,
                'deadline': drive.application_deadline.strftime('%Y-%m-%d') if drive.application_deadline else None
            })
        
        return jsonify({
            'id': company.id,
            'name': company.name,
            'email': user.email,
            'company_email': company.company_email,
            'hr_contact': company.hr_contact,
            'website': company.website,
            'industry': company.industry,
            'location': company.location,
            'registration_number': company.registration_number,
            'approval_status': company.approval_status,
            'is_active': company.is_active,
            'is_blacklisted': user.is_blacklisted,
            'created_at': company.created_at.strftime('%Y-%m-%d'),
            'drives_count': len(drives_data),
            'drives': drives_data
        })

    @app.route('/api/admin/drives', methods=['GET'])
    @jwt_required()
    def admin_list_drives():
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        search = request.args.get('search', '')
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
        except ValueError:
            page = 1
            per_page = 20
        query = PlacementDrive.query.join(Company)
        if search:
            like = f"%{search}%"
            query = query.filter((PlacementDrive.job_title.ilike(like)) | (Company.name.ilike(like)) | (Company.industry.ilike(like)))

        total = query.count()
        items = query.order_by(PlacementDrive.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
        drives = [{'id': d.id, 'title': d.job_title, 'company': d.company.name, 'status': d.status} for d in items]
        return jsonify({'items': drives, 'total': total, 'page': page, 'per_page': per_page})

    @app.route('/api/admin/drives/<int:drive_id>/approve', methods=['POST'])
    @jwt_required()
    def admin_approve_drive(drive_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        drive = PlacementDrive.query.get_or_404(drive_id)
        if drive.status != 'pending':
            return jsonify({'msg': f'Drive already {drive.status}. Cannot approve.'}), 400
        drive.status = 'approved'
        db.session.commit()
        cache.clear()
        send_enhanced_mail(
            drive.company.user.email,
            f'Drive Approved - {drive.job_title}',
            'drive_approved',
            company_name=drive.company.name,
            drive_title=drive.job_title,
            salary=drive.salary,
            deadline=drive.application_deadline.strftime('%Y-%m-%d') if drive.application_deadline else 'N/A'
        )
        return jsonify({'msg': 'Drive approved'})

    @app.route('/api/admin/drives/<int:drive_id>/reject', methods=['POST'])
    @jwt_required()
    def admin_reject_drive(drive_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        drive = PlacementDrive.query.get_or_404(drive_id)
        if drive.status != 'pending':
            return jsonify({'msg': f'Drive already {drive.status}. Cannot reject.'}), 400
        drive.status = 'rejected'
        db.session.commit()
        cache.clear()
        send_mail(drive.company.user.email, 'Drive Rejected', f'Your drive {drive.job_title} was rejected.')
        return jsonify({'msg': 'Drive rejected'})

    @app.route('/api/admin/drives/<int:drive_id>', methods=['GET'])
    @jwt_required()
    def admin_get_drive_detail(drive_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        drive = PlacementDrive.query.get_or_404(drive_id)
        applications = Application.query.filter_by(drive_id=drive.id).all()
        
        applications_data = []
        for app in applications:
            applications_data.append({
                'id': app.id,
                'student': app.student.name,
                'student_email': app.student.user.email,
                'status': app.status,
                'date': app.application_date.strftime('%Y-%m-%d')
            })
        
        return jsonify({
            'id': drive.id,
            'job_title': drive.job_title,
            'job_description': drive.job_description,
            'company_id': drive.company_id,
            'company_name': drive.company.name,
            'company_email': drive.company.company_email,
            'eligibility_criteria': drive.eligibility_criteria,
            'skills_required': drive.skills_required,
            'salary': drive.salary,
            'location': drive.location,
            'num_positions': drive.num_positions,
            'status': drive.status,
            'application_deadline': drive.application_deadline.strftime('%Y-%m-%d') if drive.application_deadline else None,
            'created_at': drive.created_at.strftime('%Y-%m-%d'),
            'applications_count': len(applications_data),
            'applications': applications_data
        })

    @app.route('/api/admin/applications', methods=['GET'])
    @jwt_required()
    def admin_list_applications():
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        search = request.args.get('search', '')
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
        except ValueError:
            page = 1
            per_page = 20

        query = Application.query.join(Student).join(PlacementDrive).join(Company)
        if search:
            like = f"%{search}%"
            query = query.filter(
                (Student.name.ilike(like)) |
                (Company.name.ilike(like)) |
                (PlacementDrive.job_title.ilike(like)) |
                (Student.user.has(User.email.ilike(like))) |
                (Application.status.ilike(like))
            )

        total = query.count()
        items = query.order_by(Application.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
        apps = []
        for a in items:
            apps.append({
                'id': a.id,
                'student': a.student.name,
                'student_email': a.student.user.email,
                'company': a.drive.company.name,
                'drive': a.drive.job_title,
                'status': a.status,
                'date': a.application_date.strftime('%Y-%m-%d')
            })
        return jsonify({'items': apps, 'total': total, 'page': page, 'per_page': per_page})

    @app.route('/api/admin/applications/<int:application_id>', methods=['GET'])
    @jwt_required()
    def admin_get_application_detail(application_id):
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        application = Application.query.get_or_404(application_id)
        
        return jsonify({
            'id': application.id,
            'student_id': application.student_id,
            'student_name': application.student.name,
            'student_email': application.student.user.email,
            'student_cgpa': application.student.cgpa,
            'student_department': application.student.department,
            'student_year': application.student.year,
            'drive_id': application.drive_id,
            'drive_title': application.drive.job_title,
            'company_id': application.drive.company_id,
            'company_name': application.drive.company.name,
            'status': application.status,
            'feedback': application.feedback,
            'application_date': application.application_date.strftime('%Y-%m-%d %H:%M'),
        })

    @app.route('/api/admin/search', methods=['GET'])
    @jwt_required()
    def admin_unified_search():
        if get_role() != 'admin':
            return jsonify({'msg': 'Unauthorized'}), 403
        search = request.args.get('q', '').strip()
        if not search:
            return jsonify({'students': [], 'companies': [], 'drives': [], 'applications': []})
        
        like = f"%{search}%"
        students = Student.query.filter(
            (Student.name.ilike(like)) | 
            (Student.department.ilike(like)) | 
            (Student.user.has(User.email.ilike(like)))
        ).limit(10).all()

        companies = Company.query.filter(
            (Company.name.ilike(like)) | 
            (Company.industry.ilike(like)) |
            (Company.location.ilike(like))
        ).limit(10).all()

        drives = PlacementDrive.query.join(Company).filter(
            (PlacementDrive.job_title.ilike(like)) | 
            (Company.name.ilike(like))
        ).limit(10).all()
        
        applications = Application.query.join(Student).join(PlacementDrive).join(Company).filter(
            (Student.name.ilike(like)) |
            (Company.name.ilike(like)) |
            (PlacementDrive.job_title.ilike(like)) |
            (Student.user.has(User.email.ilike(like))) |
            (Application.status.ilike(like))
        ).limit(10).all()
        
        return jsonify({
            'students': [{'id': s.id, 'name': s.name, 'email': s.user.email, 'type': 'student'} for s in students],
            'companies': [{'id': c.id, 'name': c.name, 'industry': c.industry, 'type': 'company'} for c in companies],
            'drives': [{'id': d.id, 'title': d.job_title, 'company': d.company.name, 'type': 'drive'} for d in drives],
            'applications': [{'id': a.id, 'student': a.student.name, 'company': a.drive.company.name, 'drive': a.drive.job_title, 'type': 'application'} for a in applications]
        })

    @app.route('/api/company/summary', methods=['GET'])
    @jwt_required()
    def company_summary():
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.filter_by(user_id=get_user_id()).first()
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        return jsonify({
            'company': company.name,
            'drives': [{'id': d.id, 'title': d.job_title, 'status': d.status} for d in drives]
        })

    @app.route('/api/company/dashboard', methods=['GET'])
    @jwt_required()
    def company_dashboard():
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.filter_by(user_id=get_user_id()).first()
        if not company:
            return jsonify({'msg': 'Company not found'}), 404
        
        user = User.query.get(get_user_id())
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        drives_data = []
        for drive in drives:
            total_applicants = Application.query.filter_by(drive_id=drive.id).count()
            approved_applicants = Application.query.filter_by(drive_id=drive.id, status='selected').count()
            drives_data.append({
                'id': drive.id,
                'job_title': drive.job_title,
                'status': drive.status,
                'total_applicants': total_applicants,
                'approved_applicants': approved_applicants,
                'salary': drive.salary,
                'location': drive.location,
                'application_deadline': drive.application_deadline.strftime('%Y-%m-%d') if drive.application_deadline else None,
                'created_at': drive.created_at.strftime('%Y-%m-%d')
            })
        
        return jsonify({
            'company': {
                'id': company.id,
                'name': company.name,
                'email': user.email,
                'company_email': company.company_email,
                'hr_contact': company.hr_contact,
                'website': company.website,
                'industry': company.industry,
                'location': company.location,
                'registration_number': company.registration_number,
                'approval_status': company.approval_status,
                'created_at': company.created_at.strftime('%Y-%m-%d')
            },
            'drives': drives_data,
            'total_drives': len(drives_data)
        })

    @app.route('/api/company/drives', methods=['POST'])
    @jwt_required()
    def company_create_drive():
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.filter_by(user_id=get_user_id()).first()
        data = request.json
        drive = PlacementDrive(
            company_id=company.id,
            job_title=data['job_title'],
            job_description=data.get('job_description'),
            eligibility_criteria=data.get('eligibility_criteria'),
            salary=data.get('salary'),
            location=data.get('location'),
            application_deadline=datetime.strptime(data['application_deadline'], '%Y-%m-%d'),
            status='pending'
        )
        db.session.add(drive)
        db.session.commit()
        return jsonify({'msg': 'Drive created, pending admin approval'})

    @app.route('/api/company/drives', methods=['GET'])
    @jwt_required()
    def company_list_drives():
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.filter_by(user_id=get_user_id()).first()
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        return jsonify([{'id': d.id, 'title': d.job_title, 'status': d.status} for d in drives])

    @app.route('/api/company/drives/<int:drive_id>/status', methods=['PUT'])
    @jwt_required()
    def company_update_drive_status(drive_id):
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        drive = PlacementDrive.query.get_or_404(drive_id)
        if drive.company.user_id != get_user_id():
            return jsonify({'msg': 'Unauthorized'}), 403
        data = request.json
        new_status = data.get('status')
        if new_status not in ['active', 'closed']:
            return jsonify({'msg': 'Invalid status. Use "active" or "closed"'}), 400
        if new_status == 'active':
            drive.status = 'approved'  
        else: 
            drive.status = 'closed' 
        
        db.session.commit()
        cache.clear()
        return jsonify({'msg': f'Drive marked as {new_status}', 'status': drive.status})

    @app.route('/api/company/drives/<int:drive_id>/applications', methods=['GET'])
    @jwt_required()
    def company_drive_applications(drive_id):
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        drive = PlacementDrive.query.get_or_404(drive_id)
        if drive.company.user_id != get_user_id():
            return jsonify({'msg': 'Unauthorized'}), 403
        applications = Application.query.filter_by(drive_id=drive.id).all()
        return jsonify([
            {'id': a.id, 'student': a.student.name, 'status': a.status, 'date': a.application_date.strftime('%Y-%m-%d')} for a in applications
        ])

    @app.route('/api/company/applications/<int:application_id>/student', methods=['GET'])
    @jwt_required()
    def company_get_applicant_profile(application_id):
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        application = Application.query.get_or_404(application_id)
        drive = PlacementDrive.query.get(application.drive_id)
        if drive.company.user_id != get_user_id():
            return jsonify({'msg': 'Unauthorized'}), 403
        student = application.student
        user = User.query.get(student.user_id)
        profile = {
            'id': student.id,
            'name': student.name,
            'email': user.email,
            'phone_number': student.phone_number,
            'college_name': student.college_name,
            'degree': student.degree,
            'department': student.department,
            'cgpa': student.cgpa,
            'year': student.year,
            'location': student.location,
            'education': student.education,
            'experience': student.experience,
            'skills': student.skills,
            'resume': student.resume,
            'is_active': student.is_active,
            'created_at': student.created_at.strftime('%Y-%m-%d') if student.created_at else None,
            'application': {
                'id': application.id,
                'status': application.status,
                'application_date': application.application_date.strftime('%Y-%m-%d') if application.application_date else None,
                'feedback': application.feedback
            }
        }
        return jsonify(profile)

    @app.route('/api/company/applications/<int:application_id>/student_resume', methods=['GET'])
    @jwt_required()
    def company_download_applicant_resume(application_id):
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        application = Application.query.get_or_404(application_id)
        drive = PlacementDrive.query.get(application.drive_id)
        if drive.company.user_id != get_user_id():
            return jsonify({'msg': 'Unauthorized'}), 403
        student = application.student
        if not student or not student.resume:
            return jsonify({'msg': 'Resume not found'}), 404
        resume_path = os.path.join(UPLOAD_FOLDER, student.resume)
        if not os.path.exists(resume_path):
            return jsonify({'msg': 'Resume file not found'}), 404
        return send_file(resume_path, as_attachment=True)

    @app.route('/api/company/applications/<int:application_id>/status', methods=['POST'])
    @jwt_required()
    def company_update_application_status(application_id):
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        application = Application.query.get_or_404(application_id)
        drive = PlacementDrive.query.get(application.drive_id)
        if drive.company.user_id != get_user_id():
            return jsonify({'msg': 'Unauthorized'}), 403
        data = request.json
        application.status = data['status']
        application.feedback = data.get('feedback')
        db.session.commit()

        email_subject = 'Application Status Updated'
        email_body = f'Your application status for {drive.job_title} is now {application.status.upper()}.'
        if data.get('date'):
            email_body += f'\n\nDate: {data.get("date")}'
        if data.get('feedback'):
            email_body += f'\n\nDetails: {data.get("feedback")}'
        send_mail(application.student.user.email, email_subject, email_body)
        return jsonify({'msg': 'Application status updated'})

    @app.route('/api/student/summary', methods=['GET'])
    @jwt_required()
    def student_summary():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.filter_by(user_id=get_user_id()).first()
        applications = Application.query.filter_by(student_id=student.id).all()
        return jsonify({
            'student': student.name,
            'applications': [{'id': a.id, 'drive': a.drive.job_title, 'status': a.status, 'date': a.application_date.strftime('%Y-%m-%d')} for a in applications]
        })

    @app.route('/api/student/drives', methods=['GET'])
    @jwt_required()
    @cache.cached(timeout=300, query_string=True)
    def student_list_drives():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.filter_by(user_id=get_user_id()).first()
        drives = PlacementDrive.query.filter(
            (PlacementDrive.status == 'approved') & 
            (PlacementDrive.application_deadline >= datetime.utcnow())
        ).all()
        eligible_drives = []
        for d in drives:
            eligible_drives.append({
                'id': d.id,
                'title': d.job_title,
                'company': d.company.name,
                'company_id': d.company.id,
                'deadline': d.application_deadline.strftime('%Y-%m-%d'),
                'salary': d.salary,
                'location': d.location
            })
        return jsonify(eligible_drives)

    @app.route('/api/student/companies', methods=['GET'])
    @jwt_required()
    def student_search_companies():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        search = request.args.get('search', '').strip()
        query = Company.query.filter(Company.approval_status == 'approved')
        if search:
            like = f"%{search}%"
            query = query.filter(
                (Company.name.ilike(like)) | 
                (Company.industry.ilike(like)) |
                (Company.location.ilike(like))
            )
        
        companies = query.limit(20).all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'industry': c.industry,
            'location': c.location,
            'website': c.website
        } for c in companies])

    @app.route('/api/student/companies/<int:company_id>', methods=['GET'])
    @jwt_required()
    def student_get_company_detail(company_id):
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.get_or_404(company_id)
        if company.approval_status != 'approved':
            return jsonify({'msg': 'Company not available'}), 403
        
        drives = PlacementDrive.query.filter(
            (PlacementDrive.company_id == company.id) &
            (PlacementDrive.status == 'approved') &
            (PlacementDrive.application_deadline >= datetime.utcnow())
        ).all()
        
        drives_data = [{
            'id': d.id,
            'job_title': d.job_title,
            'salary': d.salary,
            'location': d.location,
            'deadline': d.application_deadline.strftime('%Y-%m-%d') if d.application_deadline else None
        } for d in drives]
        return jsonify({
            'id': company.id,
            'name': company.name,
            'industry': company.industry,
            'location': company.location,
            'website': company.website,
            'hr_contact': company.hr_contact,
            'company_email': company.company_email,
            'active_drives': len(drives_data),
            'drives': drives_data
        })

    @app.route('/api/student/drives/<int:drive_id>', methods=['GET'])
    @jwt_required()
    def student_get_drive_detail(drive_id):
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        drive = PlacementDrive.query.get_or_404(drive_id)
        if drive.status != 'approved':
            return jsonify({'msg': 'Drive not available'}), 403
        
        return jsonify({
            'id': drive.id,
            'job_title': drive.job_title,
            'job_description': drive.job_description,
            'company_name': drive.company.name,
            'company_id': drive.company.id,
            'eligibility_criteria': drive.eligibility_criteria,
            'skills_required': drive.skills_required,
            'salary': drive.salary,
            'location': drive.location,
            'num_positions': drive.num_positions,
            'application_deadline': drive.application_deadline.strftime('%Y-%m-%d') if drive.application_deadline else None,
            'status': drive.status,
            'created_at': drive.created_at.strftime('%Y-%m-%d')
        })

    @app.route('/api/student/drives/<int:drive_id>/apply', methods=['POST'])
    @jwt_required()
    def student_apply_drive(drive_id):
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.filter_by(user_id=get_user_id()).first()
        drive = PlacementDrive.query.get_or_404(drive_id)
        if Application.query.filter_by(student_id=student.id, drive_id=drive.id).first():
            return jsonify({'msg': 'Already applied'}), 400
        application = Application(student_id=student.id, drive_id=drive.id)
        db.session.add(application)
        db.session.commit()
        send_mail(student.user.email, 'Application Submitted', f'You have applied for {drive.job_title}.')
        return jsonify({'msg': 'Applied successfully'})

    @app.route('/api/student/applications', methods=['GET'])
    @jwt_required()
    def student_applications():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.filter_by(user_id=get_user_id()).first()
        applications = Application.query.filter_by(student_id=student.id).all()
        return jsonify([
            {'id': a.id, 'drive': a.drive.job_title, 'company': a.drive.company.name, 'status': a.status, 'date': a.application_date.strftime('%Y-%m-%d')} for a in applications
        ])

    @app.route('/api/student/export_applications', methods=['POST'])
    @jwt_required()
    def student_export_applications():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.filter_by(user_id=get_user_id()).first()
        from tasks import export_applications_to_csv
        task = export_applications_to_csv.delay(student.id)
        return jsonify({'msg': 'Export job queued', 'job_id': task.id, 'status': 'pending'})

    @app.route('/api/student/export_status/<job_id>', methods=['GET'])
    @jwt_required()
    def student_export_status(job_id):
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        result = celery.AsyncResult(job_id)
        if result.state == 'PENDING':
            return jsonify({'status': 'pending', 'msg': 'Job is queued'})
        elif result.state == 'SUCCESS':
            return jsonify({'status': 'completed', 'download_url': f'/api/student/download_export/{job_id}'})
        elif result.state == 'FAILURE':
            return jsonify({'status': 'failed', 'msg': str(result.info)})
        else:
            return jsonify({'status': result.state})

    @app.route('/api/student/download_export/<job_id>', methods=['GET'])
    @jwt_required()
    def student_download_export(job_id):
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        
        result = celery.AsyncResult(job_id)
        if result.state == 'SUCCESS':
            csv_data = result.result
            mem = BytesIO()
            mem.write(csv_data.encode('utf-8'))
            mem.seek(0)
            return send_file(mem, mimetype='text/csv', as_attachment=True, download_name=f'applications_{job_id}.csv')
        return jsonify({'msg': 'Export not ready'}), 400

    @app.route('/api/student/profile', methods=['GET'])
    @jwt_required()
    def student_get_profile():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.filter_by(user_id=get_user_id()).first()
        user = User.query.get(get_user_id())
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        return jsonify({
            'id': student.id,
            'name': student.name,
            'email': user.email,
            'phone_number': student.phone_number,
            'college_name': student.college_name,
            'degree': student.degree,
            'department': student.department,
            'cgpa': student.cgpa,
            'year': student.year,
            'location': student.location,
            'skills': student.skills,
            'education': student.education,
            'experience': student.experience,
            'resume': student.resume
        })

    @app.route('/api/student/profile', methods=['PUT'])
    @jwt_required()
    def student_update_profile():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.filter_by(user_id=get_user_id()).first()
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        data = request.json
        student.name = data.get('name', student.name)
        student.phone_number = data.get('phone_number', student.phone_number)
        student.college_name = data.get('college_name', student.college_name)
        student.degree = data.get('degree', student.degree)
        student.department = data.get('department', student.department)
        student.cgpa = data.get('cgpa', student.cgpa)
        student.year = data.get('year', student.year)
        student.location = data.get('location', student.location)
        student.skills = data.get('skills', student.skills)
        student.education = data.get('education', student.education)
        student.experience = data.get('experience', student.experience)
        student.resume = data.get('resume', student.resume)
        db.session.commit()
        return jsonify({'msg': 'Profile updated successfully'})

    @app.route('/api/student/upload_resume', methods=['POST'])
    @jwt_required()
    def student_upload_resume():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        if 'file' not in request.files:
            return jsonify({'msg': 'No file provided'}), 400        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'msg': 'No file selected'}), 400
        if not allowed_file(file.filename):
            return jsonify({'msg': 'Only PDF, DOC, and DOCX files are allowed'}), 400
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        student = Student.query.filter_by(user_id=get_user_id()).first()
        filename = secure_filename(f"resume_{student.id}_{datetime.utcnow().timestamp()}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        student.resume = filename
        db.session.commit()
        return jsonify({'msg': 'Resume uploaded successfully', 'resume': filename})

    @app.route('/api/student/download_resume', methods=['GET'])
    @jwt_required()
    def student_download_resume():
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        student = Student.query.filter_by(user_id=get_user_id()).first()
        if not student or not student.resume:
            return jsonify({'msg': 'Resume not found'}), 404
        resume_path = os.path.join(UPLOAD_FOLDER, student.resume)
        if not os.path.exists(resume_path):
            return jsonify({'msg': 'Resume file not found'}), 404
        return send_file(resume_path, as_attachment=True)

    @app.route('/api/company/profile', methods=['GET'])
    @jwt_required()
    def company_get_profile():
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.filter_by(user_id=get_user_id()).first()
        user = User.query.get(get_user_id())
        if not company:
            return jsonify({'msg': 'Company not found'}), 404
        
        return jsonify({
            'id': company.id,
            'name': company.name,
            'email': user.email,
            'company_email': company.company_email,
            'hr_contact': company.hr_contact,
            'website': company.website,
            'industry': company.industry,
            'location': company.location,
            'registration_number': company.registration_number,
            'approval_status': company.approval_status
        })

    @app.route('/api/company/profile', methods=['PUT'])
    @jwt_required()
    def company_update_profile():
        if get_role() != 'company':
            return jsonify({'msg': 'Unauthorized'}), 403
        company = Company.query.filter_by(user_id=get_user_id()).first()
        if not company:
            return jsonify({'msg': 'Company not found'}), 404
        
        data = request.json
        company.name = data.get('name', company.name)
        company.company_email = data.get('company_email', company.company_email)
        company.hr_contact = data.get('hr_contact', company.hr_contact)
        company.website = data.get('website', company.website)
        company.industry = data.get('industry', company.industry)
        company.location = data.get('location', company.location)
        company.registration_number = data.get('registration_number', company.registration_number)
        db.session.commit()
        return jsonify({'msg': 'Company profile updated successfully'})

    @app.route('/api/drives/<int:drive_id>', methods=['GET'])
    def get_drive_details(drive_id):
        drive = PlacementDrive.query.get_or_404(drive_id)
        if drive.status != 'approved':
            return jsonify({'msg': 'Drive not available'}), 403
        
        return jsonify({
            'id': drive.id,
            'job_title': drive.job_title,
            'job_description': drive.job_description,
            'company_name': drive.company.name,
            'company_id': drive.company.id,
            'eligibility_criteria': drive.eligibility_criteria,
            'skills_required': drive.skills_required,
            'salary': drive.salary,
            'location': drive.location,
            'num_positions': drive.num_positions,
            'application_deadline': drive.application_deadline.strftime('%Y-%m-%d') if drive.application_deadline else None,
            'status': drive.status,
            'created_at': drive.created_at.strftime('%Y-%m-%d')
        })

    @app.route('/api/student/drives/<int:drive_id>/check_eligibility', methods=['GET'])
    @jwt_required()
    def check_drive_eligibility(drive_id):
        if get_role() != 'student':
            return jsonify({'msg': 'Unauthorized'}), 403
        
        student = Student.query.filter_by(user_id=get_user_id()).first()
        drive = PlacementDrive.query.get_or_404(drive_id)
        if drive.status != 'approved':
            return jsonify({'eligible': False, 'reason': 'Drive not approved'})
        if drive.application_deadline and drive.application_deadline < datetime.utcnow():
            return jsonify({'eligible': False, 'reason': 'Application deadline has passed'})
        if Application.query.filter_by(student_id=student.id, drive_id=drive.id).first():
            return jsonify({'eligible': False, 'reason': 'Already applied to this drive'})
        eligible = True
        reasons = []
        if drive.eligibility_criteria:
            criteria = drive.eligibility_criteria.lower()
            if 'cgpa' in criteria:
                try:
                    import re
                    cgpa_match = re.search(r'cgpa\s*>=?\s*(\d+\.?\d*)', criteria)
                    if cgpa_match:
                        required_cgpa = float(cgpa_match.group(1))
                        if not student.cgpa or student.cgpa < required_cgpa:
                            eligible = False
                            reasons.append(f'CGPA requirement not met (Required: {required_cgpa}, Your CGPA: {student.cgpa or "N/A"})')
                except:
                    pass
        
        return jsonify({
            'eligible': eligible,
            'reasons': reasons if reasons else ['All eligibility criteria met'],
            'student_cgpa': student.cgpa,
            'student_skills': student.skills,
            'drive_requirements': drive.eligibility_criteria
        })