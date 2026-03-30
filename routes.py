from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
import uuid
from functools import wraps

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
            if user.is_admin:
                return redirect(url_for('main.admin_dashboard'))
            return redirect(url_for('main.user_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('login.html')

    return render_template('login.html')

# decorator to protect user routes
def user_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('main.login'))
        
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('main.login'))
        
        # block admin to access user routes
        if user.is_admin:
            flash('Admins cannot access this page.', 'error')
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)
    return inner

# decorator to protect admin routes
def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('main.login'))
        
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('main.login'))
        
        # block non-admin users to access admin routes
        if not user.is_admin:
            flash('Only admins can access this page.', 'error')
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)
    return inner

@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

@main.route('/user/dashboard')
@user_required
def user_dashboard():
    if 'user_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('main.login'))
    
    user = User.query.get(session['user_id'])
    return render_template('user/user_dashboard.html', user=user)

@main.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    if 'user_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('main.login'))
    
    user = User.query.get(session['user_id'])

    return render_template('admin/admin_dashboard.html', user=user)

@main.route('/user/profile')
@user_required
def user_profile():
    user = User.query.get(session['user_id'])
    return render_template('user/user_profile.html', user=user)

@main.route('/admin/profile')
@admin_required
def admin_profile():
    user = User.query.get(session['user_id'])
    return render_template('admin/admin_profile.html', user=user)
