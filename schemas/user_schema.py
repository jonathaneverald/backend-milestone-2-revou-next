register_schema = {
    "name": {
        "type": "string",
        "required": True,
        "minlength": 3,
        "maxlength": 50
    },
    "email": {
        "type": "string",
        "required": True,
        "regex": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    },
    "password": {
        "type": "string",
        "required": True,
        "minlength": 8
    },
    "profile_pict": {
        "type": "string",
        "required": False
    },
    "disability_info": {
        "type": "dict",
        "required": False,
        "schema": {
            "accessibility_preferences": {
                "type": "string",
                "required": True
            },
            "disability_type": {
                "type": "string",
                "required": True
            }
        }
    }
}

login_email_schema = {
    "email": {
        "type": "string",
        "required": True,
        "regex": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    },
    "password": {
        "type": "string",
        "required": True
    }
}

update_profile_schema = {
    "name": {
        "type": "string",
        "required": False,
        "minlength": 3,
        "maxlength": 50
    },
    "email": {
        "type": "string",
        "required": False,
        "regex": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    },
    "password": {
        "type": "string",
        "required": False,
        "minlength": 8
    },
    "disability_info": {
        "type": "dict",
        "required": False,
        "schema": {
            "accessibility_preferences": {
                "type": "string",
                "required": True
            },
            "disability_type": {
                "type": "string",
                "required": True
            }
        }
    }
}

