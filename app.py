from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from config.config import Config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker

from db import db
from connector.mysql_connectors import connect_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = "your_secret_key_here"
    jwt = JWTManager(app)

    db.init_app(app)
    connect_db()

    @app.route("/")
    def hello_world():
        return "Hello World"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
