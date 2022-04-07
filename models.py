from datetime import timedelta

from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'latrop_boj'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://test:@localhost/jobs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = 'latrop_boj-latrop_boj'
app.config['UPLOAD_FOLDER'] = 'static'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

jwt = JWTManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


user_skills = db.Table('user_skills',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'))
                       )

job_skills = db.Table('job_skills',
                      db.Column('job_id', db.Integer, db.ForeignKey('jobs.id')),
                      db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'))
                      )


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    user = db.relationship('User', secondary=user_skills)
    job = db.relationship('Jobs', secondary=job_skills)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(120), unique=True, nullable=True)
    photo = db.Column(db.String(120), nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    skills = db.relationship('Skills', secondary=user_skills)


class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(80), nullable=False)
    job_description = db.Column(db.String(120), nullable=False)
    job_location = db.Column(db.String(120), nullable=False)
    job_salary = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    job_requirements = db.Column(db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=True)
    requirement = db.relationship('Skills', backref=db.backref('requirement', lazy=True))
    skills = db.relationship('Skills', secondary=job_skills)
    company = db.relationship('Company', backref=db.backref('company', lazy=True))
    user = db.relationship('User', backref=db.backref('user', lazy=True))


class AppliedJobs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=True)
    user = db.relationship('User', backref=db.backref('applied_jobs', lazy=True))
    job = db.relationship('Jobs', backref=db.backref('applied_jobs', lazy=True))
