from app import db
from werkzeug.security import generate_password_hash, check_password_hash
# user model
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

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    photo = db.Column(db.String(255), nullable=False)

    brand = db.Column(db.String(50), nullable=False)

    model = db.Column(db.String(100), nullable=False)

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