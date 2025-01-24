create_assessment_details_schema = {
    'assessment_id': {'type': 'integer', 'required': True},
    'title': {'type': 'string', 'required': True, 'maxlength': 100},
    'question': {'type': 'dict', 'required': True, 'maxlength': 500},
    'answer': {'type': 'dict', 'nullable': True},
    'deadline': {'type': 'datetime', 'required': True},
}

update_assessment_details_schema = {
    'title': {'type': 'string', 'maxlength': 100},
    'question': {'type': 'dict', 'maxlength': 200},
    'answer': {'type':  'dict', 'nullable': True},
    'deadline': {'type': 'datetime'},
}