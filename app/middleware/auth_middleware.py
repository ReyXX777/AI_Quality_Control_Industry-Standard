from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Callable, Optional
from datetime import datetime, timedelta
import logging
import redis
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key for JWT decoding (use environment variables in production)
SECRET_KEY = "your_secret_key"  # Replace with a strong secret key
ALGORITHM = "HS256"

# Instance of HTTPBearer for extracting token from requests
security = HTTPBearer()

# Redis connection for token blacklist and session management
REDIS_HOST = "localhost"  # Replace with your Redis host
REDIS_PORT = 6379      # Replace with your Redis port
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)


# Role-based access control component
def has_role(user_data: dict, required_role: str) -> bool:
    """
    Check if the user has the required role.
    """
    return user_data.get("role") == required_role

# Token refresh component
def refresh_token(user_data: dict) -> str:
    """
    Generate a new JWT token with an extended expiration time.
    """
    expiration = datetime.utcnow() + timedelta(hours=1)
    user_data.update({"exp": expiration})
    return jwt.encode(user_data, SECRET_KEY, algorithm=ALGORITHM)

# Token blacklist component (using Redis)
def is_token_blacklisted(token: str) -> bool:
    """
    Check if the token is blacklisted in Redis.
    """
    return redis_client.sismember("token_blacklist", token)

def add_token_to_blacklist(token: str, expiry_seconds: int = 3600): # Default expiry of 1 hour
    """
    Add a token to the Redis blacklist with an expiry.
    """
    redis_client.sadd("token_blacklist", token)
    redis_client.expire("token_blacklist", expiry_seconds) # Set expiry for the entire set.

    logger.info(f"Token blacklisted: {token}")


# Session Management Component (using Redis)
def create_session(user_data: dict) -> str:
    """
    Create a user session and store it in Redis.
    """
    session_id = str(uuid.uuid4())
    redis_client.setex(f"session:{session_id}", timedelta(hours=1), user_data) # Session expires in 1 hour
    return session_id

def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieve a user session from Redis.
    """
    return redis_client.get(f"session:{session_id}")

def delete_session(session_id: str):
    """
    Delete a user session from Redis.
    """
    redis_client.delete(f"session:{session_id}")


# Logging component for authentication events
def log_authentication_event(user_data: dict, event_type: str):
    """
    Log authentication-related events.
    """
    logger.info(f"Authentication Event - {event_type}: User {user_data.get('username')}")

async def authenticate_user(credentials: HTTPAuthorizationCredentials):
    """
    Validate JWT token and extract user information.
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


