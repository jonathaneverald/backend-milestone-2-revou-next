from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import RoleModel, EnrollmentModel
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker

from enums.enum import UserRoleEnum, RoleStatusEnum, EnrollStatusEnum

from utils.handle_response import ResponseHandler
from datetime import datetime, timedelta

from cerberus import Validator
from schemas.enrollment_schema import create_enrollment_schema, update_enrollment_schema
from schemas.role_schema import create_role_schema, update_role_schema


enrollment_bp = Blueprint("enrollment", __name__)

@enrollment_bp.route("/api/v1/institutes/<int:institute_id>/roles", methods=["POST"])
@jwt_required()
def assign_role(institute_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        validator = Validator(create_role_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)
        
        # Check if assigner is admin
        admin_role = s.query(RoleModel).filter(
                RoleModel.institute_id == institute_id,
                RoleModel.user_id == user_id,
                RoleModel.role == UserRoleEnum.admin
        ).first()
        
        if not admin_role:
            return ResponseHandler.error("Unauthorized user", 403)
            
        # Create new role
        new_role = RoleModel(
            institute_id=institute_id,
            user_id=data["user_id"],
            role=UserRoleEnum[data["role"]],
            status=RoleStatusEnum.pending
        )
        
        s.add(new_role)
        s.commit()
        
        return ResponseHandler.success(new_role.to_dictionaries(), "Role assigned successfully", 201)
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@enrollment_bp.route("/api/v1/institutes/<int:institute_id>/roles/<int:role_id>", methods=["PATCH"])
@jwt_required()
def update_role_status(institute_id, role_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        validator = Validator(update_role_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)
        
        # Check if user is admin
        admin_role = s.query(RoleModel).filter(
                RoleModel.institute_id == institute_id,
                RoleModel.user_id == user_id,
                RoleModel.role == UserRoleEnum.admin
        ).first()
        
        if not admin_role:
            return ResponseHandler.error("Unauthorized user", 403)
            
        role = s.get(RoleModel, role_id)
        if not role:
            return ResponseHandler.error("Role not found", 404)
            
        role.status = RoleStatusEnum[data["status"].lower()]
        s.commit()
        
        return ResponseHandler.success(role.to_dictionaries(), "Role status updated successfully")
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@enrollment_bp.route("/api/v1/institutes/<int:institute_id>/roles", methods=["GET"])
@jwt_required()
def get_institute_roles(institute_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        roles = s.query(RoleModel).filter(RoleModel.institute_id ==institute_id).all()
        return ResponseHandler.success(
            {"roles": [role.to_dictionaries() for role in roles]},
            "Roles retrieved successfully"
        )
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@enrollment_bp.route("/api/v1/enrollments", methods=["POST"])
@jwt_required()
def create_enrollment():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        validator = Validator(create_enrollment_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)
        
        # Verify admin role
        admin_role = s.query(RoleModel).filter(
                RoleModel.user_id == user_id,
                RoleModel.role == UserRoleEnum.admin
        ).first()
        
        if not admin_role:
            return ResponseHandler.error("Unauthorized user", 403)
            
        new_enrollment = EnrollmentModel(
            role_id=data["role_id"],
            course_id=data["course_id"],
            enrolled_at=datetime.utcnow() + timedelta(hours=7),
            status=EnrollStatusEnum.pending
        )
        
        s.add(new_enrollment)
        s.commit()
        
        return ResponseHandler.success(new_enrollment.to_dictionaries(), "Enrollment created successfully", 201)
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@enrollment_bp.route("/api/v1/enrollments", methods=["GET"])
@jwt_required()
def get_all_enrollments():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        enrollments = s.query(EnrollmentModel).all()
        return ResponseHandler.success(
            {"enrollments": [enrollment.to_dictionaries() for enrollment in enrollments]},
            "Enrollments retrieved successfully"
        )
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@enrollment_bp.route("/api/v1/enrollments/<int:enrollment_id>", methods=["GET"])
@jwt_required()
def get_enrollment_by_id(enrollment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        enrollment = s.get(EnrollmentModel, enrollment_id)
        if not enrollment:
            return ResponseHandler.error("Enrollment not found", 404)
            
        return ResponseHandler.success(enrollment.to_dictionaries(), "Enrollment retrieved successfully")
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@enrollment_bp.route("/api/v1/enrollments/<int:enrollment_id>", methods=["PATCH"])
@jwt_required()
def update_enrollment(enrollment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        validator = Validator(update_enrollment_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)
        
        # Verify admin role
        admin_role = s.query(RoleModel).filter(
                RoleModel.user_id == user_id,
                RoleModel.role == UserRoleEnum.admin
        ).first()
        if not admin_role:
            return ResponseHandler.error("Unauthorized user", 403)
            
        enrollment = s.get(EnrollmentModel, enrollment_id)
        if not enrollment:
            return ResponseHandler.error("Enrollment not found", 404)
            
        if "status" in data:
            enrollment.status = EnrollStatusEnum[data["status"].lower()]
            
        s.commit()
        
        return ResponseHandler.success(enrollment.to_dictionaries(), "Enrollment updated successfully")
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()