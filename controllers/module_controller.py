from flask import Blueprint
from flask_jwt_extended import jwt_required
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker
from models import ModuleModel, AssessmentModel, RoleModel
from utils.handle_response import ResponseHandler
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from enums.enum import UserRoleEnum
from cerberus import Validator
from schemas.module_schema import create_module_schema, update_module_schema

module_bp = Blueprint("module", __name__)


@module_bp.route("/api/v1/modules/<int:module_id>/assessments", methods=["GET"])
@jwt_required()
def get_module_assessments(module_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()

    try:
        module = s.get(ModuleModel, module_id)

        if not module:
            return ResponseHandler.error("Module not found", 404)

        # Retrieve assessments for the given module
        assessments = s.query(AssessmentModel).filter_by(module_id=module_id).all()

        assessments_data = [assessment.to_dictionaries() for assessment in assessments]

        return ResponseHandler.success({"assessments": assessments_data}, "Assessments retrieved successfully")
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    finally:
        s.close()


@module_bp.route("/api/v1/modules", methods=["POST"])
@jwt_required()
def create_module():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        validator = Validator(create_module_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Create new module
        new_module = ModuleModel(
            course_id=data["course_id"], title=data["title"], content=data["content"], module_file=data["module_file"]
        )
        s.add(new_module)
        s.commit()

        return ResponseHandler.success(new_module.to_dictionaries(), "Module created successfully", 201)

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@module_bp.route("/api/v1/modules", methods=["GET"])
@jwt_required()
def get_all_modules():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        modules = s.query(ModuleModel).filter(ModuleModel.course_id).all()

        return ResponseHandler.success(
            {"Modules": [module.to_dictionaries() for module in modules]}, "Modules retrieved successfully"
        )

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@module_bp.route("/api/v1/modules/<int:module_id>", methods=["GET"])
@jwt_required()
def get_module_by_id(module_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        module = s.get(ModuleModel, module_id)
        if not module:
            return ResponseHandler.error("module not found", 404)

        return ResponseHandler.success(module.to_dictionaries(), "module retrieved successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@module_bp.route("/api/v1/modules/<int:module_id>", methods=["PATCH"])
@jwt_required()
def update_module(module_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        module = s.get(ModuleModel, module_id)

        validator = Validator(update_module_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        if not module:
            return ResponseHandler.error("Module not found", 404)

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Update module
        if "title" in data:
            module.title = data["title"]

        if "content" in data:
            module.content = data["content"]

        if "module_file" in data:
            module.module_file = data["module_file"]

        s.commit()

        return ResponseHandler.success(module.to_dictionaries(), "Module updated successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@module_bp.route("/api/v1/modules/<int:module_id>", methods=["DELETE"])
def delete_module(module_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        module = s.get(ModuleModel, module_id)
        if not module:
            return ResponseHandler.error("Module not found", 404)

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        s.delete(module)
        s.commit()

        return ResponseHandler.success(None, "Module deleted successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()
