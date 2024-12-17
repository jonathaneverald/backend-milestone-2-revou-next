create_course_schema = {
    "role_id": {"type": "integer", "required": True, "min": 1},
    "institute_id": {"type": "integer", "required": True, "min": 1},
    "title": {"type": "string", "required": True, "minlength": 3, "maxlength": 255},
    "description": {"type": "string", "required": True, "minlength": 3, "maxlength": 255},
    "category": {"type": "string", "required": True, "minlength": 3, "maxlength": 255},
    "media": {"type": "string", "required": False, "minlength": 3, "maxlength": 255},
}

update_course_schema = {
    "title": {"type": "string", "required": True, "minlength": 3, "maxlength": 255},
    "description": {"type": "string", "required": True, "minlength": 3, "maxlength": 255},
    "category": {"type": "string", "required": True, "minlength": 3, "maxlength": 255},
    "media": {"type": "string", "required": True, "minlength": 3, "maxlength": 255},
}
