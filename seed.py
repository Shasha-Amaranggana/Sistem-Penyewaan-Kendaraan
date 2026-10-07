from app import create_app, db
from app.models import Vehicle

app = create_app()

with app.app_context():

    Vehicle.query.delete()

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
    db.session.commit()

    print("5 kendaraan berhasil dimasukkan.")