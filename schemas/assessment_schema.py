create_assessment_schema = {
    "module_id":{
        "type": "integer",
        "required": True,
        "min": 1
    },
    "type":{
        "type": "string",
        "required": True,
        "allowed": ["essay", "choices"]
    }
}

update_assessment_schema = {
    "module_id":{
        "type": "integer",
        "required": True,
        "min": 1
    },
    "type":{
        "type": "string",
        "required": True,
        "allowed": ["essay", "choices"]
    }
}

create_assessment_detail_schema = {
    "assessment_id":{
        "type": "integer",
        "required": True,
        "min": 1
    },
    "title":{
        "type": "string",
        "required": True,
        "minlength": 3,
        "maxlength": 255
    },
    "question":{
        "type": "dict",
        "required": True,
    },
    "answer":{
        "type": "dict",
        "required": True,
    },
    "deadline":{
        "type": "datetime",
        "required": True
    }
}
