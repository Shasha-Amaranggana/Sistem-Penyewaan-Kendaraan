from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User, Vehicle
from sqlalchemy import or_
from datetime import datetime
from app import db

bp = Blueprint('main', __name__)

# =========================================================
# HALAMAN OPENING
# =========================================================
@bp.route('/')
def welcome():
    return render_template('welcome.html')


# =========================================================
# HALAMAN UTAMA
# =========================================================
@bp.route('/home')
def index():

    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    vehicles = Vehicle.query.all()

    now = datetime.now()

    current_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M')

    return render_template(
        'halUtamaUser.html',
        vehicles=vehicles,
        user=user,
        current_date=current_date,
        current_time=current_time
    )


# =========================================================
# HALAMAN LOGIN | REGISTER | LOGOUT
# =========================================================
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            return redirect(url_for('main.index'))
        else:
            flash('Email atau kata sandi salah. Silakan coba lagi.')
            return redirect(url_for('main.login'))
            
    return render_template('loginRegister.html', mode='login')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        gender = request.form.get('gender')
        email = request.form.get('email')
        phone = request.form.get('phone')
        emergency_phone = request.form.get('emergency_phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Konfirmasi password tidak cocok.')
            return redirect(url_for('main.register'))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email sudah terdaftar.')
            return redirect(url_for('main.register'))

        user = User(
            name=name,
            birth_date=datetime.strptime(birth_date, '%Y-%m-%d').date(),
            gender=gender,
            email=email,
            phone=phone,
            emergency_phone=emergency_phone
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registrasi berhasil. Silakan login.')
        return redirect(url_for('main.login'))

    return render_template('loginRegister.html', mode='register')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    return redirect(url_for('main.login'))
