from flask import Blueprint
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import jwt_required, get_jwt_identity
from connector.mysql_connectors import connect_db
from models import RoleModel, EnrollmentModel, ModuleModel
from enums.enum import RoleStatusEnum
from utils.handle_response import ResponseHandler

course_bp = Blueprint("course", __name__)

@course_bp.route("/api/v1/courses/<int:course_id>/modules", methods=["GET"])
@jwt_required()
def get_course_modules(course_id):
    Session = sessionmaker(bind=connect_db())
    s = Session()
    s.begin()

    try:
        user_id = get_jwt_identity()

        # Verify user enrollment in the course
        roles = s.query(RoleModel).filter(
                    RoleModel.user_id == user_id,
                    RoleModel.role == "student",
                    RoleModel.status == RoleStatusEnum.active
                ).all()
        
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
            return ResponseHandler.success(
                {"modules": []}, "No modules found for this course."
            )

        return ResponseHandler.success(
            {"modules": [module.to_dictionaries() for module in modules]},
            "Modules retrieved successfully"
        )
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    finally:
        s.close()
