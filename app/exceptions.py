class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, 422)


class AIServiceException(AppException):
    def __init__(self, message: str = "AI service error"):
        super().__init__(message, 502)


class VectorStoreException(AppException):
    def __init__(self, message: str = "Vector store error"):
        super().__init__(message, 500)