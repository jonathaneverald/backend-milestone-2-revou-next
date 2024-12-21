from flask import Blueprint
from flask_jwt_extended import jwt_required
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker
from models import ModuleModel, AssessmentModel, RoleModel, CourseModel
from utils.handle_response import ResponseHandler
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from enums.enum import UserRoleEnum
from cerberus import Validator
from schemas.module_schema import create_module_schema, update_module_schema
from services.upload import UploadFiles
from werkzeug.datastructures import FileStorage
from flask_cors import cross_origin

module_bp = Blueprint("module", __name__)


@module_bp.route("/api/v1/modules/<int:module_id>/assessments", methods=["GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
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


@module_bp.route("/api/v1/courses/<int:course_id>/modules", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def create_module(course_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.form.to_dict()  # Change to form data to handle file upload
        module_file = request.files.get("module_file")
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

        # Check if course is available and belongs to the instructor
        course = (
            s.query(CourseModel).filter(CourseModel.id == course_id, CourseModel.role_id == instructor_role.id).first()
        )
        if not course:
            return ResponseHandler.error("Course not found or belongs to other instructor", 403)

        # Handle profile picture upload if provided
        module_file_url = None
        if module_file and isinstance(module_file, FileStorage):
            upload_files = UploadFiles()
            result = upload_files.process_single_file(module_file)

            if "error" in result:
                return ResponseHandler.error(f"Module file upload failed: {result['error']}", 400)

            module_file_url = result["file_url"]

        # Create new module
        new_module = ModuleModel(
            course_id=course_id, title=data["title"], content=data["content"], module_file=module_file_url
        )
        s.add(new_module)
        s.commit()

        return ResponseHandler.success(new_module.to_dictionaries(), "Module created successfully", 201)

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@module_bp.route("/api/v1/courses/<int:course_id>/modules", methods=["GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def get_all_modules(course_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        )
        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Check if course is available and belongs to the instructor
        course = (
            s.query(CourseModel).filter(CourseModel.id == course_id, CourseModel.role_id == instructor_role.id).first()
        )
        if not course:
            return ResponseHandler.error("Course not found or belongs to other instructor", 403)

        modules = s.query(ModuleModel).filter(ModuleModel.course_id == course.id).all()

        return ResponseHandler.success(
            {"modules": [module.to_dictionaries() for module in modules]}, "Modules retrieved successfully"
        )

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@module_bp.route("/api/v1/courses/<int:course_id>/modules/<int:module_id>", methods=["GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def get_module_by_id(course_id, module_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        # Check if course is available and belongs to the instructor
        course = s.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            return ResponseHandler.error("Course not found", 404)

        module = s.query(ModuleModel).filter(ModuleModel.id == module_id, ModuleModel.course_id == course.id).first()
        if not module:
            return ResponseHandler.error("Module not found", 404)

        return ResponseHandler.success(module.to_dictionaries(), "Module retrieved successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@module_bp.route("/api/v1/courses/<int:course_id>/modules/<int:module_id>", methods=["PATCH"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def update_module(course_id, module_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.form.to_dict()
        module_file = request.files.get("module_file")
        user_id = get_jwt_identity()

        module = s.get(ModuleModel, module_id)

        validator = Validator(update_module_schema)
        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Check if course is available and belongs to the instructor
        course = (
            s.query(CourseModel).filter(CourseModel.id == course_id, CourseModel.role_id == instructor_role.id).first()
        )
        if not course:
            return ResponseHandler.error("Course not found or belongs to other instructor", 404)

        module = s.query(ModuleModel).filter(ModuleModel.id == module_id, ModuleModel.course_id == course.id).first()
        if not module:
            return ResponseHandler.error("Module not found", 404)

        # Update module
        if "title" in data:
            module.title = data["title"]

        if "content" in data:
            module.content = data["content"]

        # Handle profile picture upload if provided
        if module_file and isinstance(module_file, FileStorage):
            upload_files = UploadFiles()
            result = upload_files.process_single_file(module_file)

            if "error" in result:
                return ResponseHandler.error(f"Module file upload failed: {result['error']}", 400)

            module.module_file = result["file_url"]

        s.commit()

        return ResponseHandler.success(module.to_dictionaries(), "Module updated successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@module_bp.route("/api/v1/courses/<int:course_id>/modules/<int:module_id>", methods=["DELETE"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def delete_module(course_id, module_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Check if course is available and belongs to the instructor
        course = (
            s.query(CourseModel).filter(CourseModel.id == course_id, CourseModel.role_id == instructor_role.id).first()
        )
        if not course:
            return ResponseHandler.error("Course not found or belongs to other instructor", 404)

        module = s.query(ModuleModel).filter(ModuleModel.id == module_id, ModuleModel.course_id == course.id).first()
        if not module:
            return ResponseHandler.error("Module not found", 404)

        s.delete(module)
        s.commit()

        return ResponseHandler.success(None, "Module deleted successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()
