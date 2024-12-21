from flask import Blueprint, request
from services.upload import UploadFiles
from werkzeug.datastructures import FileStorage
import json

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt

from models import UserModel, DisabledUserModel, InstituteModel, RoleModel
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker

from utils.handle_response import ResponseHandler

from schemas.user_schema import register_schema, login_email_schema, update_profile_schema
from cerberus import Validator

from flask_cors import cross_origin

auth_bp = Blueprint("auth", __name__)
revoked_tokens = set()


@auth_bp.route("/api/v1/auth/register", methods=["POST"])
def register():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.form.to_dict()  # Change to form data to handle file upload
        profile_pict = request.files.get("profile_pict")

        validator = Validator(register_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        # Check if user already exists
        if s.query(UserModel).filter(UserModel.email == data["email"]).first():
            return ResponseHandler.error("Email already registered", 400)

        # Handle profile picture upload if provided
        profile_pict_url = None
        if profile_pict and isinstance(profile_pict, FileStorage):
            upload_files = UploadFiles()
            result = upload_files.process_single_file(profile_pict)

            if "error" in result:
                return ResponseHandler.error(f"Profile picture upload failed: {result['error']}", 400)

            profile_pict_url = result["file_url"]

        # Create new user
        new_user = UserModel(name=data["name"], email=data["email"], profile_pict=profile_pict_url)
        new_user.set_password(data["password"])

        # Add disability info if provided
        if "disability_info" in data:
            disability = DisabledUserModel(
                accessibility_preferences=data["disability_info"]["accessibility_preferences"],
                disability_type=data["disability_info"]["disability_type"],
            )
            new_user.disabled_user = disability

        s.add(new_user)
        s.commit()

        return ResponseHandler.success(new_user.to_dictionaries(), "User registered successfully", 201)

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@auth_bp.route("/api/v1/auth/login", methods=["POST"])
def login():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()

        validator = Validator(login_email_schema)
        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        user = s.query(UserModel).filter(UserModel.email == data["email"]).first()

        if not user or not user.check_password(data["password"]):
            return ResponseHandler.error("Email or password is incorrect", 401)

        # Query user's roles and institutes
        roles_with_institutes = (
            s.query(RoleModel, InstituteModel).join(InstituteModel).filter(RoleModel.user_id == user.id).all()
        )

        roles_data = []
        for role, institute in roles_with_institutes:
            roles_data.append(
                {
                    "role": role.role.name,
                    "role_id": role.id,
                    "institute_id": institute.id,
                    "institute_name": institute.name,
                }
            )

        access_token = create_access_token(identity=str(user.id))
        return ResponseHandler.success(
            {"token": access_token, "user": user.to_dictionaries(), "roles": roles_data}, "Login successful"
        )

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@auth_bp.route("/api/v1/users/profile", methods=["GET"])
@jwt_required()
def get_profile():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        user = s.get(UserModel, user_id)

        if not user:
            return ResponseHandler.error("User not found", 404)

        return ResponseHandler.success(user.to_dictionaries(), "Profile retrieved successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@auth_bp.route("/api/v1/users/profile", methods=["PATCH"])
@jwt_required()
def update_profile():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        user = s.get(UserModel, user_id)

        if not user:
            return ResponseHandler.error("User not found", 404)

        # Handle form data and file upload
        data = request.form.to_dict()
        profile_pict = request.files.get("profile_pict")

        # Validate input data
        validator = Validator(update_profile_schema)
        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        # Handle profile picture upload if provided
        if profile_pict and isinstance(profile_pict, FileStorage):
            upload_files = UploadFiles()
            result = upload_files.process_single_file(profile_pict)

            if "error" in result:
                return ResponseHandler.error(f"Profile picture upload failed: {result['error']}", 400)

            user.profile_pict = result["file_url"]

        # Update email if provided and not already taken
        if "email" in data and data["email"] != user.email:
            existing_user = (
                s.query(UserModel).filter(UserModel.email == data["email"], UserModel.id != user_id).first()
            )

            if existing_user:
                return ResponseHandler.error("Email already taken", 400)

            user.email = data["email"]

        # Update name if provided
        if "name" in data:
            user.name = data["name"]

        # Update password if provided
        if "password" in data:
            user.set_password(data["password"])

        # Update disability info if provided
        if "disability_info" in data:
            disability_info = json.loads(data["disability_info"])  # Parse JSON string from form data

            if not user.disabled_user:
                # Create new disability info if it doesn't exist
                disability = DisabledUserModel(
                    accessibility_preferences=disability_info["accessibility_preferences"],
                    disability_type=disability_info["disability_type"],
                )
                user.disabled_user = disability
            else:
                # Update existing disability info
                user.disabled_user.accessibility_preferences = disability_info["accessibility_preferences"]
                user.disabled_user.disability_type = disability_info["disability_type"]

        s.commit()

        return ResponseHandler.success(user.to_dictionaries(), "Profile updated successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@auth_bp.route("/api/v1/users/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]  # Get the unique identifier of the JWT token
        revoked_tokens.add(jti)  # Add the token to the revoked set

        return ResponseHandler.success(message="Logged out successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)
