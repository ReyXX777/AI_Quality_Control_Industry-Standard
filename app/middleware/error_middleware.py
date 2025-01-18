from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import logging
import time
from slowapi import Limiter
from slowapi.util import get_remote_address

# Get logger instance
from config.logging import get_logger

logger = get_logger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

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

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging incoming requests and outgoing responses.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Log the incoming request
        start_time = time.time()
        logger.info(f"Incoming request: {request.method} {request.url}")

        # Process the request
        response = await call_next(request)

        # Log the outgoing response
        process_time = time.time() - start_time
        logger.info(f"Outgoing response: {response.status_code}, Process time: {process_time:.2f}s")

        return response

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate-limiting requests to prevent abuse.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check if the request exceeds the rate limit
        if limiter.is_rate_limited(request):
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests. Please try again later."}
            )

        # Process the request if within the rate limit
        response = await call_next(request)
        return response
