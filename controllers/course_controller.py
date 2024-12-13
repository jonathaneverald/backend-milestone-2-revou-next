from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import CourseModel, RoleModel
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker

from enums.enum import UserRoleEnum

from utils.handle_response import ResponseHandler

from cerberus import Validator
from schemas.course_schema import create_course_schema, update_course_schema

course_bp = Blueprint("course", __name__)

@course_bp.route("/api/v1/courses", methods=["POST"])
@jwt_required()
def create_course():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        validator = Validator(create_course_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)
        
        # Check if user is instructor
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Create new course
        new_course = CourseModel(
            institute_id=data["institute_id"],
            role_id=data["role_id"],
            title=data["title"],
            description=data["description"],
            category=data["category"],
            media=data["media"]
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
@jwt_required()
def get_all_courses():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        
        # Check if user is instructor
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)
        
        courses = s.query(CourseModel).filter(CourseModel.institute_id).all()
        return ResponseHandler.success(
            {"Courses": [course.to_dictionaries() for course in courses]},
            "Courses retrieved successfully"
        )

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@course_bp.route("/api/v1/courses/<int:course_id>", methods=["GET"])
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
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)        

        return ResponseHandler.success(course.to_dictionaries(), "Course retrieved successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@course_bp.route("/api/v1/courses/<int:course_id>", methods=["PATCH"])
@jwt_required()
def update_course(course_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        course = s.get(CourseModel, course_id)

        validator = Validator(update_course_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        if not course:
            return ResponseHandler.error("Course not found", 404)
        
        # Check if user is instructor
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

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

        # Update course media
        if "media" in data:
            course.media = data["media"]

        s.commit()

        return ResponseHandler.success(
            course.to_dictionaries(), 
            "Course updated successfully"
        )

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@course_bp.route("/api/v1/courses/<int:course_id>", methods=["DELETE"])
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
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

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