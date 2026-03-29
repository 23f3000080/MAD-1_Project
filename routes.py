from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
import uuid

# blueprint
main = Blueprint('main', __name__)

def generate_username(name):
    unique_id = str(uuid.uuid4())[:6]  # Generate a unique identifier
    return f"{name}_{unique_id}"

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        mobile_number = request.form.get('mobile_number', '').strip()

        # mandatory fields check
        if not email or not name or not password or not confirm_password or not mobile_number:
            flash('Please fill in all mandatory fields.', 'error')
            return render_template('register.html')
        
        #  check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists.', 'error')
            return render_template('register.html')

        # check password and confirm password match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        username = generate_username(name)
        hashed_password = generate_password_hash(password)

        # Create a new user and add to the database
        new_user = User(email=email, name=name, username=username, password=hashed_password, mobile_number=mobile_number)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # mandatory fields check
        if not email or not password:
            flash('Please fill in all mandatory fields.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            session['email'] = user.email
            session['name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('main.user_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@main.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('main.login'))
    
    user = User.query.get(session['user_id'])
    return render_template('user_dashboard.html', user=user)