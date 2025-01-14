from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import logging

# Get logger instance
from config.logging import get_logger

logger = get_logger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling errors globally and returning formatted responses.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            # Process the request
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the exception
            logger.error(f"Unhandled exception occurred: {str(e)}", exc_info=True)

            # Return a generic error response
            return JSONResponse(
                status_code=500,
                content={"error": "An unexpected error occurred. Please try again later."}
            )
