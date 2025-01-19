from cerberus import Validator
from models.assessment import AssesmentTypeEnum
from schemas.submission_schema import create_submission_schema
import json
from utils.handle_response import ResponseHandler

def validate_submission(data, assessment_type):
    validator = Validator(create_submission_schema)
    if validator.validate(data):
        data["answer"] = json.loads(data["answer"]) if "answer" in data else None
        print("Validation passed:", data)
    else:
        print("Validation errors:", validator.errors)

    if assessment_type == AssesmentTypeEnum.choices:
        if "answer" not in data:
            return ResponseHandler.error("`answer` is required for choices type assessments.", 400)

    if assessment_type == AssesmentTypeEnum.essay and not data.get("file"):
        return {"error": "`file` is required for essay type assessments."}, 400

    return None
