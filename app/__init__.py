from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import config


db = SQLAlchemy()
jwt = JWTManager()


def create_app(env):
    app = Flask(__name__)
    app.config.from_object(config[env])
    config[env].init_app(app)

    db.init_app(app)
    jwt.init_app(app)

    from .graphql import graphql as graphql_blueprint
    app.register_blueprint(graphql_blueprint, url_prefix='/api')

    return app
