from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the database object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configure the SQLite database
    # The database file will be created in the 'instance' folder automatically
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rentals.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-for-session-management'

    # Link the app to the database
    db.init_app(app)

    # Import routes and models inside the function to avoid circular imports
    from . import routes
    from . import models

    # Register the routes with the app
    app.register_blueprint(routes.bp)

    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
