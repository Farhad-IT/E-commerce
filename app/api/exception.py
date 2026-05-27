class AppException(Exception):
    status_code = 400

    def __init__(self, detail: str):
        self.detail = detail


class NotFoundException(AppException):
    status_code = 404

class ValidationException(AppException):
    status_code = 400

class ConflictException(AppException):
    status_code = 409

class AuthException(AppException):
    status_code = 401

class PermissionDeniedException(AppException):
    status_code = 403