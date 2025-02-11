from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config.config import Config
from flask_cors import CORS
from datetime import timedelta
import os

from db import db
from connector.mysql_connectors import connect_db

from controllers.auth_controller import auth_bp, revoked_tokens
from controllers.institute_controller import institute_bp
from controllers.enrollment_controller import enrollment_bp
from controllers.course_controller import course_bp
from controllers.module_controller import module_bp
from controllers.submission_controller import submission_bp
from controllers.assessment_controller import assessment_bp
from controllers.assessment_details_controller import assessment_details_bp
from dotenv import load_dotenv


from utils.handle_response import ResponseHandler


def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=8)
    jwt = JWTManager(app)

    CORS(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in revoked_tokens

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return ResponseHandler.error("Token has expired", 401)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return ResponseHandler.error("Request doesn't contain valid token", 401)

    db.init_app(app)
    Migrate(app, db)
    connect_db()

    register_blueprints(app)

    @app.route("/")
    def hello_world():
        return "Hello World"

    return app


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(institute_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(module_bp)
    app.register_blueprint(submission_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(assessment_details_bp)


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
