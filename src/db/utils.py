import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from src.db.core import db
from flask import current_app

def test_database_connection():
    """Test database connection with retry logic"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Simple query to test connection
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            current_app.logger.info("Database connection successful")
            return True
        except OperationalError as e:
            current_app.logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                current_app.logger.error("All database connection attempts failed")
                raise e
    return False

def init_database_with_retry(app):
    """Initialize database with retry logic"""
    with app.app_context():
        try:
            test_database_connection()
            # Only create tables if connection is successful
            db.create_all()
            current_app.logger.info("Database tables created successfully")
        except Exception as e:
            current_app.logger.error(f"Database initialization failed: {str(e)}")
            raise e
