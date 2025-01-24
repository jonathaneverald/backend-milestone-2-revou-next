from flask import Blueprint, request
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import jwt_required, get_jwt_identity
from connector.mysql_connectors import connect_db
from models import RoleModel, SubmissionModel
from enums.enum import RoleStatusEnum, UserRoleEnum
from utils.handle_response import ResponseHandler

submission_bp = Blueprint("submission", __name__)

@submission_bp.route("/api/v1/submissions/me", methods=["GET"])
@jwt_required()
def get_my_submmissions():
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()

        # Fetch roles associated with the current user
        roles = s.query(RoleModel).filter(
                    RoleModel.user_id == user_id,
                    RoleModel.role == UserRoleEnum.student,
                    RoleModel.status == RoleStatusEnum.active
                ).all()

        # Fetch submissions for these roles
        submissions = s.query(SubmissionModel).filter(
            SubmissionModel.role_id.in_([role.id for role in roles])
        ).all()

        if not submissions:
            return ResponseHandler.success(
                {"submissions": []}, "No submissions found"
            )

        # Return all the submissions
        return ResponseHandler.success(
            {"submissions": [submission.to_dictionaries() for submission in submissions]},
            "Student's submissions retrieved successfully",
        )

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@submission_bp.route("/api/v1/submissions/<int:submission_id>", methods=["GET"])
@jwt_required()
def get_submission_by_id(submission_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        # Fetch submissions by id
        submission = s.get(SubmissionModel, submission_id)

        if not submission:
            return ResponseHandler.success(
                {"submissions": []}, "No submissions found"
            )
        return ResponseHandler.success(submission.to_dictionaries(), "Submission retrieved successfully")

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()

@submission_bp.route("/api/v1/submissions/me/assessment/<int:assessment_id>", methods=["GET"])
@jwt_required()
def get_my_submission_by_assessment_id(assessment_id):  # Fixed parameter name
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()

        # Fetch roles associated with the current user
        roles = s.query(RoleModel).filter(
            RoleModel.user_id == user_id,
            RoleModel.role == UserRoleEnum.student,
            RoleModel.status == RoleStatusEnum.active
        ).all()  # Fixed unclosed parenthesis

        # Fetch submission by id
        submission = s.query(SubmissionModel).filter(
            SubmissionModel.role_id.in_([role.id for role in roles]),
            SubmissionModel.assessment_id == assessment_id
        ).first()  # Fixed incorrect parentheses and `_in_`

        if not submission:
            return ResponseHandler.success(
                {"submissions": []}, "No submissions found"
            )

        # Use `.to_dictionaries()` or equivalent method to format submission data
        return ResponseHandler.success(
            {"submissions": [submission.to_dictionaries()]},
            "Submission retrieved successfully"
        )

    except Exception as e:
        s.rollback()
        return ResponseHandler.error(str(e), 500)

    finally:
        s.close()