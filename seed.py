from app import create_app, db
from app.models import Vehicle, User
from datetime import date

app = create_app()

with app.app_context():
    # 1. HANCURKAN DAN BANGUN ULANG DATABASE
    print("Mereset database...")
    db.drop_all()
    db.create_all()

    # 2. BUAT AKUN TESTER (USER & ADMIN)
    print("Membuat akun tester...")
    
    # Akun Pelanggan Biasa
    user_biasa = User(
        name="Sana Sini",
        birth_date=date(2000, 1, 1),
        gender="Laki-laki",
        email="sanasini@gmail.com",
        phone="081234567890",
        emergency_phone="080987654321",
        role="user"
    )
    user_biasa.set_password("admin123")
    
    # Akun Admin
    admin_web = User(
        name="Bos Admin",
        birth_date=date(1990, 5, 5),
        gender="Perempuan",
        email="admin@sanasini.com",
        phone="08111222333",
        emergency_phone="08333222111",
        role="admin"
    )
    admin_web.set_password("admin123")

    db.session.add(user_biasa)
    db.session.add(admin_web)

    # 3. BUAT DATA KENDARAAN
    print("Memasukkan data kendaraan...")
    vehicles = [
        Vehicle(
            photo="rush1.png",
            brand="Toyota",
            model="Rush",
            vehicle_number="KT 1234 XX",
            year=2024,
            vehicle_type="Mobil",
            seats=7,
            luggage=2,
            price_per_day=500000,
            rental_type="Sopir & Tanpa Sopir"
        ),
        Vehicle(
            photo="avanza1.png",
            brand="Toyota",
            model="Grand New Avanza",
            vehicle_number="KT 2345 XX",
            year=2024,
            vehicle_type="Mobil",
            seats=7,
            luggage=2,
            price_per_day=450000,
            rental_type="Sopir & Tanpa Sopir"
        ),
        Vehicle(
            photo="xenia1.png",
            brand="Daihatsu",
            model="Xenia",
            vehicle_number="KT 3456 XX",
            year=2023,
            vehicle_type="Mobil",
            seats=7,
            luggage=2,
            price_per_day=400000,
            rental_type="Sopir & Tanpa Sopir"
        ),
        Vehicle(
            photo="nmax1.png",
            brand="Yamaha",
            model="NMAX",
            vehicle_number="KT 4567 XX",
            year=2024,
            vehicle_type="Motor",
            seats=2,
            luggage=1,
            price_per_day=120000,
            rental_type="Tanpa Sopir"
        ),
        Vehicle(
            photo="vario1.png",
            brand="Honda",
            model="Vario 110",
            vehicle_number="KT 5678 XX",
            year=2023,
            vehicle_type="Motor",
            seats=2,
            luggage=1,
            price_per_day=100000,
            rental_type="Tanpa Sopir"
        )
    ]

    db.session.add_all(vehicles)
    
    # 4. SIMPAN SEMUA
    db.session.commit()
    print("Berhasil! Database baru siap digunakan.")