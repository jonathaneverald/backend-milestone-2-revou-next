from cerberus import Validator
import json

def validate_answer_as_dict(field, value, error):
    # Try to parse the `answer` as JSON
    if value:
        try:
            parsed_value = json.loads(value)
            if not isinstance(parsed_value, dict):
                error(field, "Must be a valid dictionary.")
        except json.JSONDecodeError:
            error(field, "Must be a valid JSON string.")

create_submission_schema = {
    "role_id": {
        "type": "integer",
        "required": True,
        "min": 1,
        "coerce": int
    },
    "answer":{
        "type": "string",
        "required": False,
        "nullable": True,
        "check_with": validate_answer_as_dict
    },
    "file": {
        "type": "string",
        "required": False,
        "nullable": True,
        "maxlength": 255
    }
}

update_submission_schema = {
    "score": {
        "type": "integer",
        "required": False,
        "nullable": True,
        "min": 0
    }
}
