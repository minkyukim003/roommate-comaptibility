import flask_sqlalchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)

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
