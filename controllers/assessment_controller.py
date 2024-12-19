from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import AssessmentModel, RoleModel, SubmissionModel, AssessmentDetailModel
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker

from enums.enum import UserRoleEnum, AssesmentTypeEnum, RoleStatusEnum

from utils.handle_response import ResponseHandler

from cerberus import Validator
from schemas.assessment_schema import create_assessment_schema, update_assessment_schema
from schemas.submission_schema import create_submission_schema, update_submission_schema

from datetime import datetime

assessment_bp = Blueprint("assessment", __name__)

@assessment_bp.route("/api/v1/assessments", methods=["POST"])
@jwt_required()
def create_assessment():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        validator = Validator(create_assessment_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)
        
        # Check if user is instructor
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)

        # Create new assessment
        new_assessment = AssessmentModel(
            module_id=data["module_id"],
            type=AssesmentTypeEnum[data["type"]]
        )

        s.add(new_assessment)
        s.commit()

        return ResponseHandler.success(new_assessment.to_dictionaries(), "Assessment created successfully", 201)

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@assessment_bp.route("/api/v1/<int:module_id>/assessments", methods=["GET"])
@jwt_required()
def get_all_assessments_in_module(module_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        assessments = s.query(AssessmentModel).filter(AssessmentModel.module_id == module_id).all()
        return ResponseHandler.success(
            {"assessments": [assessment.to_dictionaries() for assessment in assessments]},
            "Assessments retrieved successfully"
        )

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@assessment_bp.route("/api/v1/assessments/<int:assessment_id>", methods=["GET"])
@jwt_required()
def get_assessment_by_id(assessment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        assessment = s.get(AssessmentModel, assessment_id)
        if not assessment:
            return ResponseHandler.error("Assessment not found", 404)

        return ResponseHandler.success(assessment.to_dictionaries(), "Assessment retrieved successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@assessment_bp.route("/api/v1/assessments/<int:assessment_id>", methods=["PATCH"])
@jwt_required()
def update_assessment(assessment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        assessment = s.get(AssessmentModel, assessment_id)

        validator = Validator(update_assessment_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        if not assessment:
            return ResponseHandler.error("Assessment not found", 404)
        
        # Check if user is instructor
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)
        
        # Update Assessment
        if "module_id" in data:
            assessment.module_id = data["module_id"]

        if "type" in data:
            assessment.type = AssesmentTypeEnum[data["type"]]

        s.commit()

        return ResponseHandler.success(assessment.to_dictionaries(), "Assessment updated successfully")
        
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@assessment_bp.route("/api/v1/assessments/<int:assessment_id>", methods=["DELETE"])
@jwt_required()
def delete_assessment(assessment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        assessment = s.get(AssessmentModel, assessment_id)
        if not assessment:
            return ResponseHandler.error("Assessment not found", 404)

        s.delete(assessment)
        s.commit()

        return ResponseHandler.success(None, "Assessment deleted successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@assessment_bp.route("/api/v1/assessments/<int:assessment_id>/submissions", methods=["GET"])
@jwt_required()
def get_submissions(assessment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        submission = s.get(SubmissionModel, assessment_id)
        if not submission:
            return ResponseHandler.error("Submission not found", 404)

        return ResponseHandler.success(submission.to_dictionaries(), "Submission retrieved successfully")

    except Exception as e:
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@assessment_bp.route("/api/v1/submissions/<int:submission_id>/grade", methods=["PATCH"])
@jwt_required()
def update_submission_grade(submission_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        submission = s.get(SubmissionModel, submission_id)

        validator = Validator(update_assessment_schema)

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        if not submission:
            return ResponseHandler.error("Submission not found", 404)
        
        # Check if user is instructor
        instructor_role = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.instructor
        ).first()

        if not instructor_role:
            return ResponseHandler.error("Unauthorized user", 403)
        
        # Update Assessment
        if "score" in data:
            submission.score = data["score"]

        s.commit()

        return ResponseHandler.success(submission.to_dictionaries(), "Submission updated successfully")
        
    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()


@assessment_bp.route("/api/v1/assessments/<int:assessment_id>/submissions", methods=["POST"])
@jwt_required()
def submit_assessment(assessment_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        # Validate the input payload
        validator = Validator(create_submission_schema)
        data["assessment_id"] = assessment_id

        if not validator.validate(data):
            return ResponseHandler.error("Validation error", 400, validator.errors)

        # Check if the assessment exists
        assessment = s.query(AssessmentModel).filter_by(id=assessment_id).first()
        if not assessment:
            return ResponseHandler.error("Assessment not found", 404)

        # Check user role for submission eligibility
        role = s.query(RoleModel).filter_by(
            id=data["role_id"], user_id=user_id, role=UserRoleEnum.student
        ).first()
        if not role:
            return ResponseHandler.error("Role not found or unauthorized", 403)
        
        # Check if the student role is active
        if role.status != RoleStatusEnum.active: 
            return ResponseHandler.error("Role is inactive", 403)
        
        # Check if the student has already submitted for this assessment
        existing_submission = s.query(SubmissionModel).filter_by(
            assessment_id=assessment_id, role_id=role.id
        ).first()
        if existing_submission:
            return ResponseHandler.error("You have already submitted for this assessment", 400)
        
        # Check if the deadline has passed
        assessment_detail = s.query(AssessmentDetailModel).filter_by(assessment_id=assessment_id).first()
        if assessment_detail and datetime.utcnow() > assessment_detail.deadline:    
            return ResponseHandler.error("Submission deadline has passed", 400)

        # calculate score for multiple choice assessment
        if assessment.type == AssesmentTypeEnum.choices:
            assessment_detail = s.query(AssessmentDetailModel).filter_by(
                assessment_id=assessment_id
            ).first()

            if not assessment_detail:
                return ResponseHandler.error("Assessment detail not found", 404)

            correct_answers = assessment_detail.answer
            user_answers = data.get("answer", {})
            correct_answers_count = 0
            total_questions = len(assessment_detail.question) 

            for question_number, options in assessment_detail.question.items():
                if user_answers.get(question_number) == correct_answers.get(question_number):
                    correct_answers_count += 1

            score = (correct_answers_count / total_questions) * 100
        else:
            score = None

        submission = SubmissionModel(
            assessment_id=assessment_id,
            role_id=role.id,
            file=data.get("file"),
            score=score,
            answer=user_answers
        )
        s.add(submission)
        s.commit()

        return ResponseHandler.success(submission.to_dictionaries(), "Submission created", 201)

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()