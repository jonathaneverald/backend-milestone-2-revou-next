from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.upload import UploadFiles
from werkzeug.datastructures import FileStorage
import json

from models import AssessmentModel, RoleModel, SubmissionModel, AssessmentDetailModel, UserModel
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker

from enums.enum import UserRoleEnum, AssesmentTypeEnum, RoleStatusEnum

from utils.handle_response import ResponseHandler
from utils.validate_submission import validate_submission

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

        if 'deadline' in data:
            try:
                data['deadline'] = datetime.fromisoformat(data['deadline'])
            except ValueError:
                return ResponseHandler.error("Invalid deadline format. Must be ISO 8601 (e.g., 2023-12-31T23:59:59)", 400)

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

@assessment_bp.route("/api/v1/assessments/module/<int:module_id>", methods=["GET"])
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
        submissions = s.query(SubmissionModel, UserModel.name).\
            join(UserModel, UserModel.id == SubmissionModel.role_id).\
            filter(SubmissionModel.assessment_id == assessment_id).all()

        if not submissions:
            return ResponseHandler.error("Submission not found", 404)

        submission_list = [{
            'submission_id': submission.SubmissionModel.id,
            'role_id': submission.SubmissionModel.role_id,
            'user_name': submission.name,
            'file_url': submission.SubmissionModel.file,
            'score': submission.SubmissionModel.score,
            'answer': submission.SubmissionModel.answer,
            'submitted_at': submission.SubmissionModel.submitted_at
        } for submission in submissions]

        return ResponseHandler.success(
            {"submissions": submission_list}, "Submissions retrieved successfully"
        )

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
        user_id = get_jwt_identity()
        data = request.form.to_dict()  # Change to form data to handle file upload
        submission_file = request.files.get('file')

        # Check user role for submission eligibility
        role = s.query(RoleModel).filter_by(
            id=data["role_id"], user_id=user_id, role=UserRoleEnum.student
        ).first()
        if not role:
            return ResponseHandler.error("Role not found or unauthorized", 403)
        if role.status != RoleStatusEnum.active: 
            return ResponseHandler.error("Role is inactive", 403)
        
        # Check if the student has already submitted for this assessment
        existing_submission = s.query(SubmissionModel).filter_by(
            assessment_id=assessment_id, role_id=role.id
        ).first()
        if existing_submission:
            return ResponseHandler.error("You have already submitted for this assessment", 400)

        # Check if the assessment exists
        assessment = s.query(AssessmentModel).filter_by(id=assessment_id).first()
        if not assessment:
            return ResponseHandler.error("Assessment not found", 404)
        
        assessment_type = assessment.type

        validation_error = validate_submission(data, assessment_type)
        if validation_error:
            return validation_error
        
        # Handle file upload if provided
        file_url = None
        if submission_file and isinstance(submission_file, FileStorage):
            upload_files = UploadFiles()
            result = upload_files.process_single_file(submission_file)
            
            if "error" in result:
                return ResponseHandler.error(f"File upload failed: {result['error']}", 400)
            
            file_url = result["file_url"]

        # Parse the `answer` field if provided
        user_answers = {}
        if "answer" in data:
            try:
                user_answers = data.get("answer")
            except json.JSONDecodeError:
                return ResponseHandler.error("Invalid answer format: Must be valid JSON", 400)
        
        # Check if the deadline has passed
        assessment_detail = s.query(AssessmentDetailModel).filter_by(
            assessment_id=assessment_id
        ).first()
        if assessment_detail and datetime.utcnow() > assessment_detail.deadline:    
            return ResponseHandler.error("Submission deadline has passed", 400)

        # calculate score for multiple choice assessment
        score = None
        if assessment_type == AssesmentTypeEnum.choices and user_answers:
            if not assessment_detail:
                return ResponseHandler.error("Assessment detail not found", 404)

            correct_answers = assessment_detail.answer
            correct_answers_count = 0
            total_questions = len(assessment_detail.question) 

            for question_number, options in assessment_detail.question.items():
                # Validate that question exists in both answers
                if question_number not in correct_answers:
                    return ResponseHandler.error(f"Question {question_number} not found in answer key", 500)
        
                if question_number not in user_answers:
                    continue  # Skip unanswered questions, counting them as incorrect
            
                # Compare answers only if both exist
                if user_answers[question_number] == correct_answers[question_number]:
                    correct_answers_count += 1

            score = (correct_answers_count / total_questions) * 100

        submission = SubmissionModel(
            assessment_id=assessment_id,
            role_id=role.id,
            file=file_url,
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