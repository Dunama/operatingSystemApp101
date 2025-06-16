import os 
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
    
    # Fix the DATABASE_URL parsing
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # Handle URL encoding issues
        if '%40' in db_url:
            db_url = db_url.replace('%40', '@')
        
        # Ensure the URL uses the correct scheme for psycopg2
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Updated SQLAlchemy engine options for better connection handling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'pool_size': 5,
        'max_overflow': 10,
        # 'connect_args': {
        #     'connect_timeout': 30,
        #     'sslmode': 'require'  # Required for Supabase
        # }
    }
    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-jwt-key")
    JWT_ACCESS_TOKEN_EXPIRES = 3600 #1HR
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

    # Google OAuth2 config
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    
    # For production
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv("OAUTHLIB_INSECURE_TRANSPORT", "False").lower() == "true"
    OAUTHLIB_RELAX_TOKEN_SCOPE = True