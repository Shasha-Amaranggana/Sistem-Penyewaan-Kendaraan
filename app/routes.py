from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.models import User, Vehicle, Rental, Review
from sqlalchemy import or_
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict
from functools import wraps
from app import db
import os

bp = Blueprint('main', __name__)

BULAN_ID = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
            'Agustus', 'September', 'Oktober', 'November', 'Desember']

@bp.app_template_filter('rupiah')
def rupiah(value):
    """15000 -> 15.000"""
    return f"{int(value or 0):,}".replace(',', '.')

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
# HALAMAN UTAMA USER
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
# HALAMAN PENCARIAN USER
# =========================================================
@bp.route('/hasil-pencarian')
def hasil_pencarian():

    # Ambil data dari form pencarian
    pickup_date = request.args.get('date')
    pickup_time = request.args.get('time')
    duration = request.args.get('duration', type=int)

    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    vehicle_type = request.args.get('vehicle_type', 'mobil')

    query = Vehicle.query

    if vehicle_type:
        query = query.filter(
            Vehicle.vehicle_type.ilike(vehicle_type)
        )

    if min_price is not None:
        query = query.filter(
            Vehicle.price_per_day >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Vehicle.price_per_day <= max_price
        )

    vehicles = query.all()

    # Kalau tanggal belum dikirim
    if not pickup_date:
        pickup_date = datetime.now().strftime('%d %B %Y')

    else:
        try:
            pickup_date = datetime.strptime(
                pickup_date,
                '%Y-%m-%d'
            ).strftime('%d %B %Y')

        except ValueError:
            pass

    # Kalau waktu belum dikirim
    if not pickup_time:
        pickup_time = datetime.now().strftime('%H:%M')

    # Hitung tanggal pengembalian
    if duration:
        try:
            start_date = datetime.strptime(
                request.args.get('date'),
                '%Y-%m-%d'
            )

            return_datetime = start_date + timedelta(days=duration)

            return_date = return_datetime.strftime(
                '%d %B %Y'
            )

        except (ValueError, TypeError):
            return_date = pickup_date

    else:
        return_date = pickup_date

    return_time = pickup_time

    user = None

    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    return render_template(
        'halPencarianUser.html',
        vehicles=vehicles,
        user=user,
        pickup_date=pickup_date,
        pickup_time=pickup_time,
        return_date=return_date,
        return_time=return_time,
        duration=duration,
        min_price=min_price,
        max_price=max_price,
        vehicle_type=vehicle_type
    )

@bp.route('/detail-kendaraan/<int:vehicle_id>')
def detail_kendaraan(vehicle_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # Data pencarian dibawa dari halaman sebelumnya lewat URL
    date_str = request.args.get('date')
    duration = request.args.get('duration', type=int) or 1
    pickup_time = request.args.get('time') or '10:00'

    try:
        pickup_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        pickup_date = date.today()

    end_date = pickup_date + timedelta(days=duration)
    total = vehicle.price_per_day * duration

    # Cek ketersediaan di tanggal tsb
    bentrok = Rental.query.filter(
        Rental.vehicle_id == vehicle.id,
        Rental.status.in_([Rental.STATUS_MENUNGGU, Rental.STATUS_BERJALAN]),
        Rental.start_date <= end_date,
        Rental.end_date >= pickup_date
    ).first()

    foto = request.args.get('foto', 0, type=int)
    photos = vehicle.photo_list
    if foto < 0 or foto >= len(photos):
        foto = 0

    show_reviews = request.args.get('ulasan') == '1'
    star = request.args.get('star', type=int)

    reviews = sorted(vehicle.reviews, key=lambda r: r.created_at, reverse=True)
    if star in (1, 2, 3, 4, 5):
        reviews = [r for r in reviews if r.rating == star]
    else:
        star = None

    return render_template(
        'haldetailkendaraanUser.html',
        user=user,
        vehicle=vehicle,
        pickup_date=pickup_date,
        pickup_time=pickup_time,
        end_date=end_date,
        duration=duration,
        total=total,
        tersedia=(bentrok is None),
        foto=foto,
        show_reviews=show_reviews,
        star=star,
        reviews=reviews
    )

@bp.route('/kendaraan/<int:vehicle_id>/ulasan')
def semua_ulasan(vehicle_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # Filter bintang: ?star=5 (kosong = semua)
    star = request.args.get('star', type=int)

    query = Review.query.filter_by(vehicle_id=vehicle.id)
    if star in (1, 2, 3, 4, 5):
        query = query.filter_by(rating=star)
    else:
        star = None

    reviews = query.order_by(Review.created_at.desc()).all()

    return render_template(
        'ulasanKendaraanUser.html',
        user=user,
        vehicle=vehicle,
        reviews=reviews,
        star=star
    )

PURPOSES = ['Liburan', 'Dinas / Bisnis', 'Acara keluarga', 'Pernikahan', 'Lainnya']
REGIONS = ['Dalam kota', 'Luar kota']
LOCATIONS = ['Kantor rental', 'Bandara SAMS Sepinggan']
ALLOWED_DOC_EXT = {'jpg', 'jpeg', 'png', 'pdf'}

def _save_document(file_storage, booking_code, kind):
    """Simpan KTP/SIM ke static/uploads/dokumen. Return nama file, atau None."""
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_DOC_EXT:
        return None

    folder = os.path.join(current_app.root_path, 'static', 'uploads', 'dokumen')
    os.makedirs(folder, exist_ok=True)

    filename = secure_filename(f"{booking_code}_{kind}.{ext}")
    file_storage.save(os.path.join(folder, filename))
    return filename

@bp.route('/pesanan')
def pesanan():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    vehicle_id = request.args.get('vehicle_id', type=int)

    if not vehicle_id:
        flash('Kendaraan belum dipilih.')
        return redirect(url_for('main.index'))

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    can_driver = vehicle.rental_type.startswith('Sopir')

    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    if not user:
        return redirect(url_for('main.login'))

    # Ambil data pencarian sebelumnya
    pickup_date = request.args.get('date')
    duration = request.args.get('duration', type=int)

    if not pickup_date:
        pickup_date = datetime.now().date()
    else:
        pickup_date = datetime.strptime(
            pickup_date,
            '%Y-%m-%d'
        ).date()

    if not duration:
        duration = 1

    end_date = pickup_date + timedelta(days=duration)

    def render_form(form):
        return render_template(
            'formsewaUser.html',
            user=user,
            vehicle=vehicle,
            pickup_date=pickup_date,
            end_date=end_date,
            duration=duration,
            can_driver=can_driver,
            driver_fee=Rental.DRIVER_FEE,
            accessories=Rental.ACCESSORIES,
            insurances=Rental.INSURANCES,
            purposes=PURPOSES,
            regions=REGIONS,
            locations=LOCATIONS,
            form=form,
        )

    if request.method == 'GET':
        return render_form(MultiDict())

    # ---------- POST: validasi lalu simpan ----------
    f = request.form
    with_driver = can_driver and f.get('rental_type') == 'sopir'
    accessories = [a for a in f.getlist('accessories') if a in Rental.ACCESSORIES]
    insurance = f.get('insurance') if f.get('insurance') in Rental.INSURANCES else 'dasar'
    destination = (f.get('destination_city') or '').strip()

    errors = []
    if not f.get('agree'):
        errors.append('Anda harus menyetujui syarat dan ketentuan.')
    if not destination:
        errors.append('Kota tujuan wajib diisi.')
    if not with_driver:
        for field, label in (('ktp', 'KTP'), ('sim', 'SIM')):
            up = request.files.get(field)
            if not up or not up.filename:
                errors.append(f'{label} wajib diunggah untuk sewa lepas kunci.')
            elif up.filename.rsplit('.', 1)[-1].lower() not in ALLOWED_DOC_EXT:
                errors.append(f'Format {label} harus JPG, PNG, atau PDF.')

    # Cek ulang ketersediaan (bisa saja sudah dipesan orang lain)
    bentrok = Rental.query.filter(
        Rental.vehicle_id == vehicle.id,
        Rental.status.in_([Rental.STATUS_MENUNGGU, Rental.STATUS_BERJALAN]),
        Rental.start_date <= end_date,
        Rental.end_date >= pickup_date
    ).first()
    if bentrok:
        errors.append('Maaf, kendaraan sudah dipesan pada tanggal tersebut.')

    if errors:
        for e in errors:
            flash(e)
        return render_form(f)

    # Kode booking: RMB + (1000 + nomor urut)
    last = Rental.query.order_by(Rental.id.desc()).first()
    booking_code = f"RMB{1000 + (last.id if last else 0) + 1}"

    rental = Rental(
        booking_code=booking_code,
        user_id=user.id,
        vehicle_id=vehicle.id,
        start_date=pickup_date,
        end_date=end_date,
        status=Rental.STATUS_MENUNGGU,
        with_driver=with_driver,
        accessories=','.join(accessories),
        insurance=insurance,
        purpose=f.get('purpose'),
        region=f.get('region'),
        destination_city=destination,
        pickup_location=f.get('pickup_location'),
        return_location=f.get('return_location'),
        special_request=(f.get('special_request') or '').strip() or None,
    )

    if not with_driver:
        rental.ktp_file = _save_document(request.files.get('ktp'), booking_code, 'ktp')
        rental.sim_file = _save_document(request.files.get('sim'), booking_code, 'sim')

    db.session.add(rental)
    db.session.commit()

    flash(f'Pesanan {booking_code} berhasil dibuat. Menunggu konfirmasi admin.')
    return redirect(url_for('main.index'))   


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


# =========================================================
# HALAMAN ADMIN: DAFTAR KENDARAAN
# =========================================================
@bp.route('/admin/kendaraan')
@admin_required
def admin_kendaraan():
    # ---------- KARTU STATISTIK ----------
    total_vehicles = Vehicle.query.count()
    rented_vehicle_ids = {r.vehicle_id for r in
                          Rental.query.filter_by(status=Rental.STATUS_BERJALAN).all()}

    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Vehicle.query
    if q:
        pattern = f'%{q}%'
        query = query.filter(or_(
            Vehicle.brand.ilike(pattern),
            Vehicle.model.ilike(pattern),
        ))

    pagination = query.order_by(Vehicle.id.desc()).paginate(
        page=page, per_page=5, error_out=False)
    
    return render_template(
        'admin/kendaraan_list.html',
        active_menu='kendaraan',
        total_vehicles=total_vehicles,
        rented_vehicle_ids=rented_vehicle_ids,
        pagination=pagination,
        q=q,
        statuses=Rental.ALL_STATUS,
        **admin_context()
    )

# =========================================================
# HALAMAN ADMIN: TAMBAH KENDARAAN
# =========================================================
@bp.route('/admin/kendaraan/tambah', methods=['GET', 'POST'])
@admin_required
def tambah_kendaraan():
    if request.method == 'POST':
        foto = request.files.get('photo')
        filename = "default.png"
        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            foto.save(os.path.join('app', 'static', 'images', filename))

        new_vehicle = Vehicle(
            photo=filename,
            brand=request.form.get('merek'),
            model=request.form.get('tipe'),
            year=request.form.get('tahun'),
            color=request.form.get('warna'),
            vehicle_number=request.form.get('plat_nomor'),
            rental_type=request.form.get('jenis_penyewaan'),
            fuel=request.form.get('bahan_bakar'),          # Menggunakan fuel sesuai models_2.py
            transmission=request.form.get('transmisi'),
            vehicle_type=request.form.get('kategori'),     # Menggunakan vehicle_type sesuai models_2.py
            price_per_day=request.form.get('harga_sewa'),
            seats=request.form.get('jumlah_penumpang'),
            luggage=request.form.get('jumlah_bagasi'),
            chassis_number=request.form.get('no_rangka'),
            engine_number=request.form.get('no_mesin'),
            is_active=True # Default aktif
        )
        db.session.add(new_vehicle)
        try:
            db.session.commit()
            flash('Kendaraan berhasil ditambahkan.')
            return redirect(url_for('main.admin_kendaraan'))
        except Exception as e:
            db.session.rollback()
            flash('Gagal menambahkan kendaraan. Pastikan Plat/Rangka/Mesin tidak duplikat.')
            
    return render_template('admin/kendaraan_tambah.html', active_menu='kendaraan', **admin_context())

# =========================================================
# HALAMAN ADMIN: EDIT KENDARAAN
# =========================================================
@bp.route('/admin/kendaraan/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_kendaraan(id):
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        foto = request.files.get('photo')
        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            foto.save(os.path.join('app', 'static', 'images', filename))
            vehicle.photo = filename

        vehicle.brand = request.form.get('merek')
        vehicle.model = request.form.get('tipe')
        vehicle.year = request.form.get('tahun')
        vehicle.color = request.form.get('warna')
        vehicle.vehicle_number = request.form.get('plat_nomor')
        vehicle.rental_type = request.form.get('jenis_penyewaan')
        vehicle.fuel = request.form.get('bahan_bakar')          # Sesuai models_2.py
        vehicle.transmission = request.form.get('transmisi')
        vehicle.vehicle_type = request.form.get('kategori')     # Sesuai models_2.py
        vehicle.price_per_day = request.form.get('harga_sewa')
        vehicle.seats = request.form.get('jumlah_penumpang')
        vehicle.luggage = request.form.get('jumlah_bagasi')
        vehicle.chassis_number = request.form.get('no_rangka')
        vehicle.engine_number = request.form.get('no_mesin')
        vehicle.notes = request.form.get('catatan_kondisi')     # Menggunakan notes sesuai models_2.py
        
        # Checkbox aktif
        vehicle.is_active = True if request.form.get('is_active') else False

        try:
            db.session.commit()
            flash('Data kendaraan berhasil diperbarui.')
            return redirect(url_for('main.admin_kendaraan'))
        except Exception as e:
            db.session.rollback()
            flash('Gagal mengedit kendaraan. Data duplikat.')

    return render_template('admin/kendaraan_edit.html', active_menu='kendaraan', vehicle=vehicle, **admin_context())


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
