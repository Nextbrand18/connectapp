from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
photos = UploadSet('photos', IMAGES)
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    configure_uploads(app, photos)
    
    from .routes import main
    app.register_blueprint(main)
    
    # Import models here to avoid circular imports
    from . import models
    
    # Register CLI commands
    register_cli_commands(app)
    
    return app

def register_cli_commands(app):
    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database."""
        with app.app_context():
            db.create_all()
            print("Initialized the database!")