create_assessment_details_schema = {
    'assessment_id': {'type': 'integer', 'required': True},
    'title': {'type': 'string', 'required': True, 'maxlength': 100},
    'question': {'type': 'string', 'required': True, 'maxlength': 200},
    'answer': {'type': ['string', 'dict', 'list'], 'nullable': True},
    'deadline': {'type': 'datetime', 'required': True},
}

update_assessment_details_schema = {
    'title': {'type': 'string', 'maxlength': 100},
    'question': {'type': 'string', 'maxlength': 200},
    'answer': {'type': ['string', 'dict', 'list'], 'nullable': True},
    'deadline': {'type': 'datetime'},
    'updated_at': {'type': 'datetime'}
}