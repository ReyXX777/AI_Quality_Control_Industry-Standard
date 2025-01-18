from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Callable, Optional
from datetime import datetime, timedelta

# Secret key for JWT decoding (use environment variables in production)
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Instance of HTTPBearer for extracting token from requests
security = HTTPBearer()

# Role-based access control component
def has_role(user_data: dict, required_role: str) -> bool:
    """
    Check if the user has the required role.

    Args:
        user_data (dict): Decoded token data containing user details.
        required_role (str): The role required to access the resource.

    Returns:
        bool: True if the user has the required role, otherwise False.
    """
    return user_data.get("role") == required_role

# Token refresh component
def refresh_token(user_data: dict) -> str:
    """
    Generate a new JWT token with an extended expiration time.

    Args:
        user_data (dict): Decoded token data containing user details.

    Returns:
        str: A new JWT token.
    """
    expiration = datetime.utcnow() + timedelta(hours=1)
    user_data.update({"exp": expiration})
    return jwt.encode(user_data, SECRET_KEY, algorithm=ALGORITHM)

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

def auth_middleware(next: Callable, required_role: Optional[str] = None):
    """
    Middleware to check authentication and role-based access for protected routes.

    Args:
        next (Callable): The next function to execute if authentication is valid.
        required_role (str, optional): The role required to access the resource.

    Returns:
        Callable: Wrapped function with authentication and role-checking logic.
    """
    async def wrapper(request: Request):
        # Extract credentials using HTTPBearer
        credentials = await security(request)
        if not credentials:
            raise HTTPException(status_code=401, detail="Authorization token is missing")

        # Validate the token and inject user information into the request state
        user_data = await authenticate_user(credentials)
        request.state.user = user_data

        # Check role-based access if required
        if required_role and not has_role(user_data, required_role):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # Proceed to the next middleware or endpoint
        return await next(request)
    
    return wrapper
