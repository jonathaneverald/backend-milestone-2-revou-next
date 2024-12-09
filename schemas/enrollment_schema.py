create_enrollment_schema = {
    "role_id": {
        "type": "integer",
        "required": True,
        "min": 1
    },
    "course_id": {
        "type": "integer",
        "required": True,
        "min": 1
    }
}

update_enrollment_schema = {
    "status": {
        "type": "string",
        "required": True,
        "allowed": ["passed", "pending", "accepted"]
    }
}
