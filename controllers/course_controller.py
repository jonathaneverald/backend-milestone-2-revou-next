from flask import Blueprint
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import jwt_required, get_jwt_identity
from connector.mysql_connectors import connect_db
from models import RoleModel, EnrollmentModel, ModuleModel, CourseModel
from enums.enum import RoleStatusEnum, UserRoleEnum
from utils.handle_response import ResponseHandler
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from cerberus import Validator
from schemas.course_schema import create_course_schema, update_course_schema
from services.upload import UploadFiles
from werkzeug.datastructures import FileStorage
from flask_cors import cross_origin

course_bp = Blueprint("course", __name__)


@course_bp.route("/api/v1/student-courses/<int:course_id>/modules", methods=["GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def get_course_modules(course_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()

        # Verify user enrollment in the course
        roles = (
            s.query(RoleModel)
            .filter(
                RoleModel.user_id == user_id, RoleModel.role == "student", RoleModel.status == RoleStatusEnum.active
            )
            .all()
        )

        enrolled = (
            s.query(EnrollmentModel)
            .filter(
                EnrollmentModel.role_id.in_([role.id for role in roles]),
                EnrollmentModel.course_id == course_id,
            )
            .all()
        )

        if not enrolled:
            return ResponseHandler.error("Student is not enrolled in this course or the student is inactive.", 403)

        # Fetch modules for the course
        modules = s.query(ModuleModel).filter(ModuleModel.course_id == course_id).all()

        if not modules:
            return ResponseHandler.success({"modules": []}, "No modules found for this course.")

        return ResponseHandler.success(
            {"modules": [module.to_dictionaries() for module in modules]}, "Modules retrieved successfully"
        )
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    finally:
        s.close()


@course_bp.route("/api/v1/courses", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def create_course():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.form.to_dict()
        user_id = get_jwt_identity()
        media = request.files.get("media")
        data["role_id"] = int(data["role_id"])
        data["institute_id"] = int(data["institute_id"])

        validator = Validator(create_course_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Handle media files upload if provided
        media_url = None
        if media and isinstance(media, FileStorage):
            upload_files = UploadFiles()
            result = upload_files.process_single_file(media)

            if "error" in result:
                return ResponseHandler.error(f"Media upload failed: {result['error']}", 400)

            media_url = result["file_url"]

        # Create new course
        new_course = CourseModel(
            institute_id=data["institute_id"],
            role_id=data["role_id"],
            title=data["title"],
            description=data["description"],
            category=data["category"],
            media=media_url,
        )
        s.add(new_course)
        s.commit()

        return ResponseHandler.success(new_course.to_dictionaries(), "Course created successfully", 201)

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@course_bp.route("/api/v1/courses", methods=["GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def get_all_courses():
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

        courses = s.query(CourseModel).filter(CourseModel.institute_id == instructor_role.institute_id).all()
        return ResponseHandler.success(
            {"Courses": [course.to_dictionaries() for course in courses]}, "Courses retrieved successfully"
        )

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@course_bp.route("/api/v1/courses/<int:course_id>", methods=["GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def get_course_by_id(course_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        course = s.get(CourseModel, course_id)
        if not course:
            return ResponseHandler.error("Course not found", 404)

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        return ResponseHandler.success(course.to_dictionaries(), "Course retrieved successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@course_bp.route("/api/v1/courses/<int:course_id>", methods=["PATCH"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def update_course(course_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.form.to_dict()
        user_id = get_jwt_identity()
        media = request.files.get("media")

        course = s.get(CourseModel, course_id)

        validator = Validator(update_course_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        if not course:
            return ResponseHandler.error("Course not found", 404)

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel)
            .filter(
                RoleModel.user_id == user_id,
                RoleModel.role == UserRoleEnum.instructor,
                RoleModel.institute_id == course.institute_id,
            )
            .first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Update course title
        if "title" in data:
            course.title = data["title"]

        # Update course description
        if "description" in data:
            course.description = data["description"]

        # Update course category
        if "category" in data:
            course.category = data["category"]

        # Handle media files upload if provided
        if media and isinstance(media, FileStorage):
            upload_files = UploadFiles()
            result = upload_files.process_single_file(media)

            if "error" in result:
                return ResponseHandler.error(f"Media upload failed: {result['error']}", 400)

            course.media = result["file_url"]

        s.commit()

        return ResponseHandler.success(course.to_dictionaries(), "Course updated successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@course_bp.route("/api/v1/courses/<int:course_id>", methods=["DELETE"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def delete_course(course_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        course = s.get(CourseModel, course_id)

        if not course:
            return ResponseHandler.error("Course not found", 404)

        # Check if user is instructor
        instructor_role = (
            s.query(RoleModel)
            .filter(
                RoleModel.user_id == user_id,
                RoleModel.role == UserRoleEnum.instructor,
                RoleModel.institute_id == course.institute_id,
            )
            .first()
        )

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        s.delete(course)
        s.commit()

        return ResponseHandler.success(None, "Course deleted successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@course_bp.route("/api/v1/institute-courses/<int:institute_id>", methods=["GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
@jwt_required()
def show_all_courses(institute_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()

        # # Check if user is instructor
        # instructor_role = (
        #     s.query(RoleModel).filter(RoleModel.user_id == user_id, RoleModel.role == UserRoleEnum.instructor).first()
        # )

        # if not instructor_role:
        #     return ResponseHandler.error("Unauthorized user", 403)

        courses = s.query(CourseModel).filter(CourseModel.institute_id == institute_id).all()
        return ResponseHandler.success(
            {"Courses": [course.to_dictionaries() for course in courses]}, "Courses retrieved successfully"
        )

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()
