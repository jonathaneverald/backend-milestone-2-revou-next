create_submission_schema = {
    "assessment_id": {
        "type": "integer",
        "required": True,
        "min": 1
    },
    "role_id": {
        "type": "integer",
        "required": True,
        "min": 1
    },
    "score": {
        "type": "integer",
        "required": False,
        "nullable": True,
        "min": 0
    },
    "answer":{
        "type": "dict",
        "required": True,
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
    },
    "file": {
        "type": "string",
        "required": False,
        "nullable": True,
        "maxlength": 255
    }
}
