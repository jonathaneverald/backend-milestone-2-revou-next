from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from connector.mysql_connectors import connect_db
from sqlalchemy.orm import sessionmaker
from models import ModuleModel, AssessmentModel
from utils.handle_response import ResponseHandler

module_bp = Blueprint("module", __name__)

@module_bp.route("/api/v1/modules/<int:module_id>/assessments", methods=["GET"])
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
        
        return ResponseHandler.success(
            {"assessments": assessments_data},
            "Assessments retrieved successfully"
        )
    except Exception as e:
        return ResponseHandler.error(str(e), 500)
    finally:
        s.close()
