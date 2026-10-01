from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Vehicle, User
from . import db

bp = Blueprint('main', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        else:
            flash('Email atau kata sandi salah!')
            
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))

@bp.route('/')
def index():
    # Cek apakah user sudah login
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
        
    vehicles = Vehicle.query.all()
    return render_template('index.html', vehicles=vehicles)
