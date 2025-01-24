from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import AssessmentModel, AssessmentDetailModel, RoleModel
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker

from enums.enum import UserRoleEnum, AssesmentTypeEnum

from utils.handle_response import ResponseHandler

from cerberus import Validator
from schemas.assessment_details_schema import create_assessment_details_schema, update_assessment_details_schema

assessment_details_bp = Blueprint("assessment_details", __name__)

@assessment_details_bp.route("/api/v1/assessments_details/<int:assessment_id>", methods=["POST"])
@jwt_required()
def create_assessment_details(assessment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        validator = Validator(create_assessment_details_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        assessment = s.query(AssessmentModel).filter_by(assessment_id=assessment_id).first()

        if not assessment:
            return ResponseHandler.error("Assessment not found", 404)
        
        # Check if assessment type is Choices or Essay
        assessment_type = assessment.type
    
        if assessment_type == AssesmentTypeEnum.choices and 'answer' not in data:
            return ResponseHandler.error('Answer is required for choices assessment type', 400)
        
        # Check if user is instructor
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)


        assessment_detail = AssessmentDetailModel(
            assessment_id=data['assessment_id'],
            title=data['title'],
            question=data['question'],
            answer=data['answer'] if 'answer' in data else None,
            deadline=data['deadline'],
        )

        s.add(assessment_detail)
        s.commit()

        return ResponseHandler.success(assessment_detail.to_dictionaries(), "Assessment created successfully", 201)

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@assessment_details_bp.route("/api/v1/assessments_details/<int:assessment_id>", methods=["GET"])
@jwt_required()
def get_assessment_details_by_asssesment_id(assessment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()
        assessment_details = s.query(AssessmentDetailModel).filter_by(assessment_id=assessment_id).first()
        if not assessment_details:
            return ResponseHandler.error("Create the assesment details first!", 404)
        
        # Check if the user is an instructor and has access to this assessment details
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)


        return ResponseHandler.success(assessment_details.to_dictionaries(), "Assessment retrieved successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@assessment_details_bp.route("/api/v1/assessment_details/<int:assessment_id>", methods=["PATCH"])
@jwt_required()
def update_assessment_details_by_assessment(assessment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        validator = Validator(update_assessment_details_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        assessment_details = s.query(AssessmentDetailModel).filter_by(assessment_id=assessment_id).first()
        if not assessment_details:
            return ResponseHandler.error("Assestment details not found", 404)
        
        # Check if user is instructor
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)
        
        if not assessment_details:
            return ResponseHandler.error('Assessment detail not found', 404 )

        for key, value in data.items():
            setattr(assessment_details, key, value)

        s.commit()

        return ResponseHandler.success(assessment_details.to_dictionaries(), "Assessment updated successfully")
        
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()