from app import create_app, db
from app.models import User, Vehicle

app = create_app()

with app.app_context():
    # 1. Hapus dan buat ulang tabel database
    db.drop_all()
    db.create_all()

    # 2. Buat akun tester
    print("Membuat akun tester (sanasini@gmail.com)...")
    tester = User(name="Sana Sini", email="sanasini@gmail.com")
    tester.set_password("admin123")
    db.session.add(tester)

    # 3. Buat data dummy kendaraan (dengan transmisi)
    print("Membuat data kendaraan...")
    vehicles = [
        Vehicle(brand="Toyota", model="Rush", price_per_day=500000, seats=6, transmission="AT"),
        Vehicle(brand="Daihatsu", model="Xenia", price_per_day=450000, seats=6, transmission="MT"),
        Vehicle(brand="Toyota", model="Innova", price_per_day=650000, seats=6, transmission="AT"),
        Vehicle(brand="Honda", model="CRV", price_per_day=850000, seats=4, transmission="AT"),
        Vehicle(brand="Toyota", model="Avanza", price_per_day=500000, seats=6, transmission="MT"),
        Vehicle(brand="Daihatsu", model="Sigra", price_per_day=350000, seats=6, transmission="MT")
    ]
    db.session.bulk_save_objects(vehicles)
    
    # Simpan ke database
    db.session.commit()
    print("Data berhasil dimasukkan! Database siap digunakan.")
