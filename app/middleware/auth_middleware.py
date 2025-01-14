from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Callable

# Secret key for JWT decoding (use environment variables in production)
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Instance of HTTPBearer for extracting token from requests
security = HTTPBearer()

async def authenticate_user(credentials: HTTPAuthorizationCredentials):
    """
    Validate JWT token and extract user information.

    Args:
        credentials (HTTPAuthorizationCredentials): Token extracted from the request.

    Returns:
        dict: Decoded token data containing user details.
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def auth_middleware(next: Callable):
    """
    Middleware to check authentication for protected routes.

    Args:
        next (Callable): The next function to execute if authentication is valid.

    Returns:
        Callable: Wrapped function with authentication logic.
    """
    async def wrapper(request: Request):
        # Extract credentials using HTTPBearer
        credentials = await security(request)
        if not credentials:
            raise HTTPException(status_code=401, detail="Authorization token is missing")

        # Validate the token and inject user information into the request state
        user_data = await authenticate_user(credentials)
        request.state.user = user_data

        # Proceed to the next middleware or endpoint
        return await next(request)
    
    return wrapper
