from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.string_model import db

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    from app import routes
    routes.register_routes(app)
    return app
