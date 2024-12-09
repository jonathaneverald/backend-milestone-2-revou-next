create_role_schema = {
    "user_id": {
        "type": "integer",
        "required": True,
        "min": 1
    },
    "role": {
        "type": "string",
        "required": True,
        "allowed": ["instructor", "student"]
    }
}

update_role_schema = {
    "status": {
        "type": "string",
        "required": True,
        "allowed": ["active", "inactive", "pending"]
    }
}
