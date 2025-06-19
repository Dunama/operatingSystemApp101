from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance to be imported by other modules
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    # Create all tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created or verified.")


