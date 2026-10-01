from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError


def create_error_response(
    status_code: int,
    message: str,
    error_type: str,
    details: list = None
) -> dict:
    """Standard error response format."""
    response = {
        "success": False,
        "error": {
            "code": status_code,
            "message": message,
            "type": error_type
        }
    }
    if details:
        response["error"]["details"] = details
    return response


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    """
    Handles all HTTPException errors.
    Converts to our standard format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.detail,
            error_type=get_error_type(exc.status_code)
        )
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handles Pydantic validation errors (422).
    Makes them readable and consistent.
    """
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=422,
            message="Validation failed. Please check your input.",
            error_type="VALIDATION_ERROR",
            details=errors
        )
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handles unexpected database errors.
    Never exposes DB details to client.
    """
    # Log the real error (in production use proper logging)
    print(f"DATABASE ERROR: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=500,
            message="A database error occurred. Please try again.",
            error_type="DATABASE_ERROR"
        )
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Catches ANY unexpected error.
    Last line of defence.
    Never exposes internal details.
    """
    # Log the real error
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=500,
            message="An unexpected error occurred. Please try again.",
            error_type="INTERNAL_SERVER_ERROR"
        )
    )


def get_error_type(status_code: int) -> str:
    """Map status code to error type string."""
    types = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR"
    }
    return types.get(status_code, "ERROR")