from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Callable, Optional
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Token blacklist component
TOKEN_BLACKLIST = set()

def is_token_blacklisted(token: str) -> bool:
    """
    Check if the token is blacklisted.

    Args:
        token (str): The JWT token to check.

    Returns:
        bool: True if the token is blacklisted, otherwise False.
    """
    return token in TOKEN_BLACKLIST

def add_token_to_blacklist(token: str):
    """
    Add a token to the blacklist.

    Args:
        token (str): The JWT token to blacklist.
    """
    TOKEN_BLACKLIST.add(token)
    logger.info(f"Token blacklisted: {token}")

# Logging component for authentication events
def log_authentication_event(user_data: dict, event_type: str):
    """
    Log authentication-related events.

    Args:
        user_data (dict): Decoded token data containing user details.
        event_type (str): The type of event (e.g., "login", "token_refresh").
    """
    logger.info(f"Authentication Event - {event_type}: User {user_data.get('username')}")

async def authenticate_user(credentials: HTTPAuthorizationCredentials):
    """
    Validate JWT token and extract user information.

    Args:
        credentials (HTTPAuthorizationCredentials): Token extracted from the request.

    Returns:
        dict: Decoded token data containing user details.
    """
    try:
        # Check if the token is blacklisted
        if is_token_blacklisted(credentials.credentials):
            raise HTTPException(status_code=401, detail="Token is blacklisted")

        # Decode the JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        log_authentication_event(payload, "login")
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
