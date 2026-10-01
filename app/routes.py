from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User, Vehicle
from sqlalchemy import or_
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Cek apakah user sudah login
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    # Ambil data user yang sedang login
    user = User.query.get(session['user_id'])
    
    # Dapatkan waktu sekarang
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M')
        
    query = Vehicle.query
    
    # Ambil parameter dari form filter (GET)
    transmissions = request.args.getlist('transmission')
    capacities = request.args.getlist('capacity')
    
    # 1. Logika Filter Transmisi
    if transmissions:
        query = query.filter(Vehicle.transmission.in_(transmissions))
        
    # 2. Logika Filter Kapasitas
    if capacities:
        capacity_filters = []
        if '4' in capacities:
            capacity_filters.append(Vehicle.seats <= 5) # Mobil 4-5 kursi
        if '6' in capacities:
            capacity_filters.append(Vehicle.seats >= 6) # Mobil 6+ kursi
            
        if capacity_filters:
            query = query.filter(or_(*capacity_filters))
            
    # Eksekusi query
    vehicles = query.all()
    
    return render_template('index.html', vehicles=vehicles, user=user,
                           selected_transmissions=transmissions, 
                           selected_capacities=capacities,
                           current_date=current_date,
                           current_time=current_time)

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
            
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))
