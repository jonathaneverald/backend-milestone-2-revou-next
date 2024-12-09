from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import InstituteModel, RoleModel
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker

from enums.enum import UserRoleEnum
from utils.handle_response import ResponseHandler

from cerberus import Validator
from schemas.institute_schema import create_institute_schema, update_institute_schema

institute_bp = Blueprint("institute", __name__)

@institute_bp.route("/api/v1/institutes", methods=["POST"])
@jwt_required()
def create_institute():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        validator = Validator(create_institute_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)
        
        # Create new institute
        new_institute = InstituteModel(
            name=data["name"]
        )
        s.add(new_institute)
        s.flush()  # Get the institute ID
        
        # Create admin role for the creator
        admin_role = RoleModel(
            institute_id=new_institute.id,
            user_id=user_id,
            role=UserRoleEnum.admin
        )
        s.add(admin_role)
        s.commit()
        
        return ResponseHandler.success(new_institute.to_dictionaries(), "Institute created successfully", 201)
        
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@institute_bp.route("/api/v1/institutes", methods=["GET"])
@jwt_required()
def get_all_institutes():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        institutes = s.query(InstituteModel).all()
        return ResponseHandler.success(
            {"institutes": [institute.to_dictionaries() for institute in institutes]},
            "Institutes retrieved successfully"
        )
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@institute_bp.route("/api/v1/institutes/<int:institute_id>", methods=["GET"])
@jwt_required()
def get_institute_by_id(institute_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        institute = s.get(InstituteModel, institute_id)
        if not institute:
            return ResponseHandler.error("Institute not found", 404)
            
        return ResponseHandler.success(institute.to_dictionaries(), "Institute retrieved successfully")
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@institute_bp.route("/api/v1/institutes/<int:institute_id>", methods=["PATCH"])
@jwt_required()
def update_institute(institute_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        institute = s.get(InstituteModel, institute_id)

        validator = Validator(update_institute_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)
        
        if not institute:
            return ResponseHandler.error("Institute not found", 404)
            
        # Check if user is admin
        admin_role = s.query(RoleModel).filter(
            (
                RoleModel.institute_id == institute_id,
                RoleModel.user_id == user_id,
                RoleModel.role == UserRoleEnum.admin
            )
        ).first()
        
        if not admin_role:
            return ResponseHandler.error("Unauthorized user", 403)
            
        data = request.get_json()
        institute.name = data.get("name", institute.name)
        s.commit()
        
        return ResponseHandler.success(institute.to_dictionaries(), "Institute updated successfully")
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()

@institute_bp.route("/api/v1/institutes/<int:institute_id>", methods=["DELETE"])
@jwt_required()
def delete_institute(institute_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        institute = s.get(InstituteModel, institute_id)
        
        if not institute:
            return ResponseHandler.error("Institute not found", 404)
            
        # Check if user is admin
        admin_role = s.query(RoleModel).filter(
            (
                RoleModel.institute_id == institute_id,
                RoleModel.user_id == user_id,
                RoleModel.role == UserRoleEnum.admin
            )
        ).first()
        
        if not admin_role:
            return ResponseHandler.error("Unauthorized user", 403)
            
        s.delete(institute)
        s.commit()
        
        return ResponseHandler.success(message="Institute deleted successfully")
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)
    
    finally:
        s.close()
