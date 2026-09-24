from . import db

# This class will automatically become a database table!
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    # This is how the object prints out in the terminal (useful for debugging)
    def __repr__(self):
        return f"<Vehicle {self.brand} {self.model}>"
