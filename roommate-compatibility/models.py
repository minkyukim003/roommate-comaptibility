# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))

    profile = db.relationship("UserProfile", uselist=False, back_populates="user")
    quiz = db.relationship("QuizResponse", uselist=False, back_populates="user")

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    major = db.Column(db.String(120))
    hobbies = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='profile')  # FIXED HERE

    # Quiz scores
    cleanliness = db.Column(db.Integer)
    sleep_schedule = db.Column(db.Integer)
    noise_tolerance = db.Column(db.Integer)
    guest_frequency = db.Column(db.Integer)
    communication_style = db.Column(db.Integer)
    financial_habits = db.Column(db.Integer)
    pet_friendliness = db.Column(db.Integer)
    cooking_frequency = db.Column(db.Integer)
    work_study_hours = db.Column(db.Integer)
    smoking_preferences = db.Column(db.Integer)
