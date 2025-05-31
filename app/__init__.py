from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_wtf.csrf import CSRFProtect
import os

db = SQLAlchemy()
login_manager = LoginManager()
photos = UploadSet('photos', IMAGES)
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    configure_uploads(app, photos)

    from .routes import main
    app.register_blueprint(main)

    return app
