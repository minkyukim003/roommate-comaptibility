from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Quiz scores
    clean = db.Column(db.Float)
    sleep_sch = db.Column(db.Float)
    noise_tole = db.Column(db.Float)
    guest_freq = db.Column(db.Float)
    communication = db.Column(db.Float)
    financial = db.Column(db.Float)
    pet_friend = db.Column(db.Float)
    cook_freq = db.Column(db.Float)
    work_hr = db.Column(db.Float)
    smoking_freq = db.Column(db.Float)

    # Optional profile stuff
    bio = db.Column(db.Text)
    profile_picture_url = db.Column(db.String(250))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
