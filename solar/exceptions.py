from rest_framework.exceptions import ValidationError


class BadRequestException(ValidationError):
    def __init__(self, detail=None, ok=False):
        self.detail = {
            'error_note': detail,
            'ok': ok,
            'result': ''
        }
