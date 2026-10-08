from app import create_app, db
from app.models import Vehicle, User, Rental
from datetime import date, datetime, timedelta

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
    db.session.flush()  # supaya vehicle.id sudah terisi

    # 4. BUAT PELANGGAN CONTOH
    print("Membuat pelanggan contoh...")
    customers = []
    for i, (nama, gender) in enumerate([
        ("Budi Santoso", "Laki-laki"),
        ("Udin Saputra", "Laki-laki"),
        ("Yanto Wijaya", "Laki-laki"),
        ("Adit Pratama", "Laki-laki"),
    ], start=1):
        c = User(
            name=nama,
            birth_date=date(1998, i, 10),
            gender=gender,
            email=f"{nama.split()[0].lower()}@gmail.com",
            phone=f"08120000000{i}",
            emergency_phone=f"08130000000{i}",
            role="user"
        )
        c.set_password("user123")
        customers.append(c)
    db.session.add_all(customers)
    db.session.flush()

    # 5. BUAT DATA PENYEWAAN CONTOH
    print("Membuat data penyewaan...")
    budi, udin, yanto, adit = customers
    rush, avanza, xenia, nmax, vario = vehicles
    now = datetime.now()

    rental_data = [
        # (pelanggan, kendaraan, tgl sewa, tgl kembali, status, dibuat berapa hari lalu)
        (budi,      rush,   date(2026, 10, 1),  date(2026, 10, 4),  "Selesai",  7),
        (udin,      rush,   date(2026, 10, 3),  date(2026, 10, 7),  "Selesai",  6),
        (yanto,     xenia,  date(2026, 10, 5),  date(2026, 10, 9),  "Berjalan", 5),
        (adit,      avanza, date(2026, 10, 7),  date(2026, 10, 15), "Batal",    4),
        (budi,      nmax,   date(2026, 10, 7),  date(2026, 10, 10), "Berjalan", 3),
        (user_biasa, vario, date(2026, 10, 10), date(2026, 10, 12), "Menunggu", 1),
        (udin,      avanza, date(2026, 10, 11), date(2026, 10, 14), "Menunggu", 0),
        (yanto,     rush,   date(2026, 10, 12), date(2026, 10, 13), "Menunggu", 0),
    ]

    rentals = []
    for idx, (cust, veh, start, end, status, days_ago) in enumerate(rental_data, start=1):
        rentals.append(Rental(
            booking_code=f"RMB{1000 + idx}",
            user_id=cust.id,
            vehicle_id=veh.id,
            start_date=start,
            end_date=end,
            status=status,
            created_at=now - timedelta(days=days_ago, minutes=idx)
        ))
    db.session.add_all(rentals)
    
    # 6. SIMPAN SEMUA
    db.session.commit()
    print("Berhasil! Database baru siap digunakan.")