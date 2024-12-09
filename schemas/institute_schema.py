create_institute_schema = {
    "name": {
        "type": "string",
        "required": True,
        "minlength": 3,
        "maxlength": 255
    }
}

update_institute_schema = {
    "name": {
        "type": "string",
        "required": True,
        "minlength": 3,
        "maxlength": 255
    }
}
