from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import logging
import time
from slowapi import Limiter
from slowapi.util import get_remote_address
import uuid
from prometheus_client import Counter, Histogram

# Get logger instance
from config.logging import get_logger

logger = get_logger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

# Prometheus Metrics
request_counter = Counter('http_requests_total', 'Total number of HTTP requests')
request_latency = Histogram('http_request_latency_seconds', 'Latency of HTTP requests')
error_counter = Counter('http_errors_total', 'Total number of HTTP errors')


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
            error_counter.inc() # Increment error counter

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
        request_id = str(uuid.uuid4())  # Generate request ID here
        request.state.request_id = request_id  # Store in request state
        logger.info(f"Request ID: {request_id} - Incoming request: {request.method} {request.url}")
        request_counter.inc() # Increment request counter

        # Process the request
        response = await call_next(request)

        # Log the outgoing response
        process_time = time.time() - start_time
        logger.info(f"Request ID: {request_id} - Outgoing response: {response.status_code}, Process time: {process_time:.2f}s")
        response.headers["X-Request-ID"] = request_id # Add to Response headers
        request_latency.observe(process_time) # Observe latency

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


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Process the request
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

