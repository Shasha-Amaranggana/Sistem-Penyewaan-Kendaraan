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
    
    # ========== FILTER DARI SIDEBAR ==========
    transmissions = request.args.getlist('transmission')
    capacities = request.args.getlist('capacity')
    
    if transmissions:
        query = query.filter(Vehicle.transmission.in_(transmissions))
        
    if capacities:
        capacity_filters = []
        if '4' in capacities:
            capacity_filters.append(Vehicle.seats <= 5)
        if '6' in capacities:
            capacity_filters.append(Vehicle.seats >= 6)
        if capacity_filters:
            query = query.filter(or_(*capacity_filters))
    
    # ========== FILTER DARI SEARCH BAR ==========
    # 1. Filter Harga Maksimum (Slider)
    max_price = request.args.get('max_price', type=int)
    if max_price:
        query = query.filter(Vehicle.price_per_day <= max_price)
    
    # 2. Filter Pencarian Nama Mobil (Keyword)
    search_query = request.args.get('q', '').strip()
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            or_(
                Vehicle.brand.ilike(search_pattern),
                Vehicle.model.ilike(search_pattern)
            )
        )
    
    # 3. Sorting (Urutkan berdasarkan)
    sort_by = request.args.get('sort', 'default')
    if sort_by == 'price_asc':
        query = query.order_by(Vehicle.price_per_day.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Vehicle.price_per_day.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(Vehicle.brand.asc(), Vehicle.model.asc())
            
    # Eksekusi query
    vehicles = query.all()
    
    return render_template('index.html', vehicles=vehicles, user=user,
                           selected_transmissions=transmissions, 
                           selected_capacities=capacities,
                           current_date=current_date,
                           current_time=current_time,
                           max_price=max_price or 1000000,
                           search_query=search_query,
                           sort_by=sort_by)

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
    session.pop('user_name', None)
    session.pop('user_email', None)
    return redirect(url_for('main.login'))
