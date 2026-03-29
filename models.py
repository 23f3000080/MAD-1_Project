from flask_sqlalchemy import SQLAlchemy

# instantiate the SQLAlchemy object
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    is_admin = db.Column(db.Boolean, default=False) #0-user, 1-admin
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
