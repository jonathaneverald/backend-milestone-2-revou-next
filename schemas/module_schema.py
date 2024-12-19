create_module_schema = {
    # "course_id": {
    #     "type": "integer",
    #     "required": True,
    #     "min": 1
    # },
    "title": {"type": "string", "required": True, "minlength": 3, "maxlength": 255},
    "content": {"type": "string", "required": True, "minlength": 3},
    "module_file": {"type": "string", "required": False, "minlength": 3, "maxlength": 255},
}

update_module_schema = {
    "title": {"type": "string", "required": False, "minlength": 3, "maxlength": 100},
    "content": {"type": "string", "required": False, "minlength": 3},
    "module_file": {"type": "string", "required": False, "minlength": 3, "maxlength": 255},
}
