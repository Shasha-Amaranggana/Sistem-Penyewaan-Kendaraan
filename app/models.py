from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# =========================================================
# USER MODEL (Class User)
# =========================================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    emergency_phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Kolom baru untuk membedakan Admin dan User
    role = db.Column(db.String(20), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# =========================================================
# KENDARAAN MODEL (Class Vehicle)
# =========================================================
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    gallery = db.Column(db.Text, nullable=True)  
    vehicle_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )
    year = db.Column(db.Integer, nullable=False)
    vehicle_type = db.Column(
        db.String(20),
        nullable=False
    )
    seats = db.Column(db.Integer, nullable=False)
    luggage = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )
    price_per_day = db.Column(
        db.Integer,
        nullable=False
    )
    rental_type = db.Column(
        db.String(30),
        nullable=False
    )

    color = db.Column(db.String(30), nullable=True)
    chassis_number = db.Column(db.String(50), unique=True, nullable=True)
    engine_number = db.Column(db.String(50), unique=True, nullable=True)
    fuel = db.Column(db.String(20), nullable=True, default='Bensin')
    transmission = db.Column(db.String(20), nullable=True, default='Manual')
    engine_cc = db.Column(db.Integer, nullable=True)
    facilities = db.Column(db.Text, nullable=True)   
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def full_name(self):
        return f"{self.brand} {self.model}"

    @property
    def facility_list(self):
        if not self.facilities:
            return []
        return [f.strip() for f in self.facilities.split(',')]

    @property
    def photo_list(self):
        photos = [self.photo]
        if self.gallery:
            photos += [p.strip() for p in self.gallery.split(',')]
        return photos

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def avg_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    def rating_count(self, star):
        return sum(1 for r in self.reviews if r.rating == star)

    def rating_percent(self, star):
        if not self.reviews:
            return 0
        return round(self.rating_count(star) / len(self.reviews) * 100)

    @property
    def latest_reviews(self):
        return sorted(self.reviews, key=lambda r: r.created_at, reverse=True)[:2]
    
    @property
    def current_status(self):
        """Cek status kendaraan di tabel Rental"""
        active_rental = Rental.query.filter_by(vehicle_id=self.id, status=Rental.STATUS_BERJALAN).first()
        if active_rental:
            return "Disewa"
        return "Tersedia"

# =========================================================
# RENTAL MODEL (Data Penyewaan)
# =========================================================
class Rental(db.Model):
    # Daftar status yang valid
    STATUS_MENUNGGU = 'Menunggu'
    STATUS_BERJALAN = 'Berjalan'
    STATUS_SELESAI = 'Selesai'
    STATUS_BATAL = 'Batal'
    ALL_STATUS = [STATUS_MENUNGGU, STATUS_BERJALAN, STATUS_SELESAI, STATUS_BATAL]

    DRIVER_FEE = 150000                       
    ACCESSORIES = {                           
        'kursi_bayi':   ('Kursi Bayi (Baby Car Seat)', 15000),
        'phone_holder': ('Phone holder', 5000),
        'bantal':       ('Bantal', 5000),
        'selimut':      ('Selimut', 10000),
    }
    INSURANCES = {                          
        'dasar':   ('Dasar', 0),
        'lengkap': ('Lengkap', 50000),
    }

    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(20), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_MENUNGGU)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    with_driver = db.Column(db.Boolean, nullable=False, default=False)
    accessories = db.Column(db.String(200), nullable=True, default='')  
    insurance = db.Column(db.String(20), nullable=False, default='dasar')
    purpose = db.Column(db.String(50), nullable=True)
    region = db.Column(db.String(30), nullable=True)
    destination_city = db.Column(db.String(100), nullable=True)
    pickup_location = db.Column(db.String(100), nullable=True)
    return_location = db.Column(db.String(100), nullable=True)
    special_request = db.Column(db.Text, nullable=True)
    ktp_file = db.Column(db.String(255), nullable=True)
    sim_file = db.Column(db.String(255), nullable=True)

    # Relasi antar objek (OOP): rental.user dan rental.vehicle
    user = db.relationship('User', backref=db.backref('rentals', lazy=True))
    vehicle = db.relationship('Vehicle', backref=db.backref('rentals', lazy=True))

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    @property
    def accessory_keys(self):
        return [k for k in (self.accessories or '').split(',') if k in self.ACCESSORIES]

    @property
    def vehicle_cost(self):
        return self.duration_days * self.vehicle.price_per_day

    @property
    def driver_cost(self):
        return self.duration_days * self.DRIVER_FEE if self.with_driver else 0

    @property
    def accessories_cost(self):
        return sum(self.ACCESSORIES[k][1] for k in self.accessory_keys)

    @property
    def insurance_cost(self):
        price = self.INSURANCES.get(self.insurance or 'dasar', ('', 0))[1]
        return price * self.duration_days

    @property
    def total_price(self):
        return self.duration_days * self.vehicle.price_per_day

# =========================================================
# REVIEW MODEL (Ulasan Pengguna)
# =========================================================
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)   # 1 sampai 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    vehicle = db.relationship('Vehicle', backref=db.backref('reviews', lazy=True))