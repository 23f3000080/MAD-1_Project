from flask import Flask
from models import db
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# app initialization
app = Flask(__name__)

# database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')


# initialize the database with the app
db.init_app(app)

# import and register blueprints
from routes import main
app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
