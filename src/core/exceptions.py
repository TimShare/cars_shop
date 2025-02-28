from fastapi import HTTPException, status


class NotFoundError(Exception):
    """Raised when a resource is not found."""

    pass


class DuplicateEntryError(Exception):
    """Raised when a unique constraint is violated."""

    pass


class AlreadyExists(Exception):
    """Raised when a unique constraint is violated."""

    pass


class InvalidCredentials(Exception):
    """Raised when invalid credentials are provided."""

    pass


class TokenExpiredError(Exception):
    """Raised when the token has expired."""

    pass


class InvalidTokenError(Exception):
    """Raised when the token is invalid."""

    pass


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidCredentials(HTTPException):
    def __init__(self, detail: str = "Invalid Credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredError(HTTPException):
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenError(HTTPException):
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidRequestError(HTTPException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedClientError(HTTPException):
    def __init__(self, detail: str = "Unauthorized client"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidGrantError(HTTPException):
    def __init__(self, detail: str = "Invalid grant"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnsupportedGrantTypeError(HTTPException):
    def __init__(self, detail: str = "Unsupported grant type"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidScopeError(HTTPException):
    def __init__(self, detail: str = "Invalid scope"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
