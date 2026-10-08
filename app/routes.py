from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User, Vehicle, Rental
from sqlalchemy import or_
from datetime import datetime, date
from functools import wraps
from app import db

bp = Blueprint('main', __name__)

BULAN_ID = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
            'Agustus', 'September', 'Oktober', 'November', 'Desember']


@bp.app_template_filter('tanggal_id')
def tanggal_id(value):
    """Format tanggal ke Bahasa Indonesia, contoh: 01 Oktober 2026"""
    if not value:
        return '-'
    return f"{value.day:02d} {BULAN_ID[value.month - 1]} {value.year}"

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
            session['user_role'] = user.role  # Simpan jabatan di session
            
            # POLISI LALU LINTAS (If-Else Role)
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Email atau kata sandi salah. Silakan coba lagi.')
            return redirect(url_for('main.login'))
            
    return render_template('loginRegister.html', mode='login')

# =========================================================
# HALAMAN ADMIN
# =========================================================
def admin_required(view_func):
    """Decorator: hanya user dengan role 'admin' yang boleh masuk."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            flash('Anda tidak memiliki akses ke halaman ini!')
            return redirect(url_for('main.login'))
        return view_func(*args, **kwargs)
    return wrapper


def admin_context():
    """Data yang dipakai bersama oleh semua halaman admin (navbar & notifikasi)."""
    pending = (Rental.query
               .filter_by(status=Rental.STATUS_MENUNGGU)
               .order_by(Rental.created_at.desc())
               .all())
    return {
        'admin': User.query.get(session['user_id']),
        'pending_rentals': pending,
    }


@bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    today = date.today()

    # ---------- KARTU STATISTIK ----------
    total_vehicles = Vehicle.query.count()
    rented_vehicle_ids = {r.vehicle_id for r in
                          Rental.query.filter_by(status=Rental.STATUS_BERJALAN).all()}
    available_vehicles = total_vehicles - len(rented_vehicle_ids)

    running = Rental.query.filter_by(status=Rental.STATUS_BERJALAN).count()
    waiting = Rental.query.filter_by(status=Rental.STATUS_MENUNGGU).count()
    active_total = running + waiting

    new_today = (Rental.query
                 .filter(Rental.status == Rental.STATUS_MENUNGGU,
                         db.func.date(Rental.created_at) == today.isoformat())
                 .count())

    # ---------- TABEL PENYEWAAN TERBARU (search + pagination) ----------
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Rental.query.join(User).join(Vehicle)
    if q:
        pattern = f'%{q}%'
        query = query.filter(or_(
            Rental.booking_code.ilike(pattern),
            User.name.ilike(pattern),
            Vehicle.brand.ilike(pattern),
            Vehicle.model.ilike(pattern),
        ))

    pagination = query.order_by(Rental.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False)

    return render_template(
        'admin/dashboard.html',
        active_menu='dashboard',
        total_vehicles=total_vehicles,
        available_vehicles=available_vehicles,
        active_total=active_total,
        running=running,
        waiting=waiting,
        new_today=new_today,
        pagination=pagination,
        q=q,
        statuses=Rental.ALL_STATUS,
        **admin_context()
    )


@bp.route('/admin/penyewaan/<int:rental_id>/status', methods=['POST'])
@admin_required
def admin_update_rental_status(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    new_status = request.form.get('status')

    if new_status not in Rental.ALL_STATUS:
        flash('Status tidak valid.')
    else:
        rental.status = new_status
        db.session.commit()
        flash(f'Status {rental.booking_code} diubah menjadi "{new_status}".')

    return redirect(request.referrer or url_for('main.admin_dashboard'))


@bp.route('/admin/kendaraan')
@admin_required
def admin_kendaraan():
    return render_template('admin/placeholder.html', active_menu='kendaraan',
                           title='Kendaraan', icon='fa-car', **admin_context())


@bp.route('/admin/penyewaan')
@admin_required
def admin_penyewaan():
    return render_template('admin/placeholder.html', active_menu='penyewaan',
                           title='Penyewaan', icon='fa-file-signature', **admin_context())


@bp.route('/admin/pelanggan')
@admin_required
def admin_pelanggan():
    return render_template('admin/placeholder.html', active_menu='pelanggan',
                           title='Pelanggan', icon='fa-users', **admin_context())


@bp.route('/admin/sopir')
@admin_required
def admin_sopir():
    return render_template('admin/placeholder.html', active_menu='sopir',
                           title='Sopir', icon='fa-id-card', **admin_context())

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
    session.pop('user_role', None)
    return redirect(url_for('main.login'))
