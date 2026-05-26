from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', uselist=False, backref='user')
    company = db.relationship('Company', uselist=False, backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    hr_contact = db.Column(db.String(120))
    company_email = db.Column(db.String(120))
    website = db.Column(db.String(120))
    industry = db.Column(db.String(120))
    location = db.Column(db.String(120))
    registration_number = db.Column(db.String(120))
    approval_status = db.Column(db.String(20), default='pending')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    drives = db.relationship('PlacementDrive', backref='company', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(15))
    college_name = db.Column(db.String(120))
    degree = db.Column(db.String(120))
    department = db.Column(db.String(120))
    cgpa = db.Column(db.Float)
    year = db.Column(db.Integer)
    location = db.Column(db.String(120))
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    resume = db.Column(db.String(256))
    skills = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)