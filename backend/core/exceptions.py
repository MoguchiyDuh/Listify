from typing import Optional


class ListifyException(Exception):
    """Base exception for all Listify errors"""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class NotFound(ListifyException):
    """Resource not found exception"""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} with identifier '{identifier}' not found"
        super().__init__(status_code=404, detail=detail)


class PermissionDenied(ListifyException):
    """Permission denied exception"""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=403, detail=detail)


class AlreadyExists(ListifyException):
    """Resource already exists exception"""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        detail = f"{resource} already exists"
        if identifier:
            detail = f"{resource} with identifier '{identifier}' already exists"
        super().__init__(status_code=409, detail=detail)


class ValidationError(ListifyException):
    """Validation error exception"""

    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class Unauthorized(ListifyException):
    """Unauthorized access exception"""

    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=401, detail=detail)


class Forbidden(ListifyException):
    """Forbidden access exception"""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=403, detail=detail)
