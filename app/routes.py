from flask import Blueprint, render_template
from .models import Vehicle

# Create a Blueprint for routing
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Fetch all vehicles from the database using OOP queries!
    vehicles = Vehicle.query.all()
    
    # Pass the vehicles to the HTML template
    return render_template('index.html', vehicles=vehicles)
