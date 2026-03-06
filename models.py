from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class Company(db.Model):
    id = db.Column(db.Integer,
                db.ForeignKey('user.id'),
                primary_key=True)
    name = db.Column(db.String(100))
    hr_contact = db.Column(db.Integer)
    website = db.Column(db.String(200))
    approved = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)

class Student(db.Model):
    id = db.Column(db.Integer,
                db.ForeignKey('user.id'),
                primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    skills = db.Column(db.String(200))
    resume = db.Column(db.String(200))
    blacklisted = db.Column(db.Boolean, default=False)

class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer,
                        db.ForeignKey('company.id'))

    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    deadline = db.Column(db.String(100))
    approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="Pending")

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,
                        db.ForeignKey('student.id'))
    drive_id = db.Column(db.Integer,
                        db.ForeignKey('drive.id'))
    status = db.Column(db.String(20),default="Applied")
    application_date = db.Column( db.Date, default=datetime.date.today)
    __table_args__ = (
        db.UniqueConstraint('student_id','drive_id'),
    )
