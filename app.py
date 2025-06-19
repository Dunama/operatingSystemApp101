from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from src.config import Config
from src.db.core import db, init_db
import os

# Import auth_bp and init_oauth BEFORE create_app
from src.api.auth.auth import auth_bp, init_oauth

def create_app():
    app = Flask(__name__,
                static_folder='src/static',
                template_folder='src/templates')
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] 
    
    # Import models here to avoid circular imports
    from src.db.models.users import User
    from src.db.models.quiz_db import Questions, Answers, Options, Response
    
    # Initialize the database and create tables
    init_db(app)  # This will handle db.init_app(app) and db.create_all()
    init_oauth(app)    # Only create migrate in development
    migrate = Migrate(app, db)

    with app.app_context():        # Import models
        from src.db.models.quiz_db import Questions, Options, Answers, Response
        from src.db.models.users import User
        # Import blueprints
        from src.api.models.quiz_route import quiz_bp
        from src.api.models.demoRun import demo_bp
        from src.api.models.practiceQuiz import practice_bp
        from src.api.models.questionBank import comprehensive_bp
        from src.api.models.paystack import paystack_bp
        from src.api.admin.admin import admin_bp
        from src.api.auth.auth import auth_bp

        # Register blueprints without url_prefix
        app.register_blueprint(quiz_bp)
        app.register_blueprint(demo_bp)
        app.register_blueprint(practice_bp)
        app.register_blueprint(comprehensive_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(paystack_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')

        # Add error handlers
        # @app.errorhandler(404)
        # def not_found_error(error):
        #     print(f"404 error: {error}")
        #     return redirect(url_for('auth.login'))

    return app  

# For Vercel
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)