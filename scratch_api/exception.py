from rest_framework.exceptions import APIException, ValidationError, _get_error_details


class DuplicateUsername(APIException):
    status_code = 400
    default_detail = 'user with this username already exists!!!.'
    default_code = '20'

