from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from config.config import Config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS

from db import db
from connector.mysql_connectors import connect_db
from models.user import UserModel
from models.disabled_user import DisabledUserModel
from models.institute import InstituteModel
from models.role import RoleModel
from models.course import CourseModel
from models.module import ModuleModel
from models.assessment import AssessmentModel
from models.assessment_detail import AssessmentDetailModel
from models.enrollment import EnrollmentModel
from models.submission import SubmissionModel


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = "your_secret_key_here"
    jwt = JWTManager(app)

    CORS(
        app,
        origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        supports_credentials=True,
        methods=["*"],
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization", "XCSRF-Token"],
    )

    db.init_app(app)
    Migrate(app, db)
    connect_db()

    register_blueprints(app)

    @app.route("/")
    def hello_world():
        return "Hello World"

    return app


def register_blueprints(app):
    pass
    # Register blueprints here


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
