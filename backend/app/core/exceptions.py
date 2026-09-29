import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


class SaaSForgeError(Exception):
    """Base exception for all custom errors."""

    code: str = "INTERNAL_ERROR"
    message: str = "An internal error occurred."
    status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        status_code: int | None = None,
    ):
        if message:
            self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(SaaSForgeError):
    code = "NOT_FOUND"
    message = "The requested resource does not exist."
    status_code = 404


class ValidationError(SaaSForgeError):
    code = "VALIDATION_ERROR"
    message = "The request data is invalid."
    status_code = 422


class UnauthorizedError(SaaSForgeError):
    code = "UNAUTHORIZED"
    message = "Authentication is required to access this resource."
    status_code = 401


class ForbiddenError(SaaSForgeError):
    code = "FORBIDDEN"
    message = "You do not have permission to access this resource."
    status_code = 403


class QuotaExceededError(SaaSForgeError):
    code = "QUOTA_EXCEEDED"
    message = "Plan quota exceeded."
    status_code = 402


async def saasforge_exception_handler(request: Request, exc: SaaSForgeError) -> JSONResponse:
    logger.warning("domain_exception", code=exc.code, message=exc.message, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                # "request_id": request.state.request_id
                # if hasattr(request.state, "request_id") else None
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
    )
