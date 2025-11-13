"""
JWT Authentication Handler
Provides token generation, validation, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
import os
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key_here_change_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))


class JWTHandler:
    """JWT token management"""

    @staticmethod
    def create_access_token(
        user_id: str,
        email: str,
        role: str = "user",
        marina_id: Optional[str] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token

        Args:
            user_id: Unique user identifier
            email: User email address
            role: User role (admin, marina_manager, staff, user)
            marina_id: Associated marina ID
            expires_delta: Token expiration time

        Returns:
            JWT token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)

        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "marina_id": marina_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        logger.info(f"Access token created for user {user_id} (role: {role})")

        return token

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Create JWT refresh token (longer expiry)

        Args:
            user_id: Unique user identifier

        Returns:
            JWT refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=30)

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded payload

        Raises:
            jwt.ExpiredSignatureError: Token has expired
            jwt.InvalidTokenError: Token is invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise

    @staticmethod
    def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user information from token

        Args:
            token: JWT token string

        Returns:
            User information dict or None if invalid
        """
        try:
            payload = JWTHandler.verify_token(token)
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "marina_id": payload.get("marina_id")
            }
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None


class PasswordHandler:
    """Password hashing and verification"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare

        Returns:
            True if passwords match
        """
        return pwd_context.verify(plain_password, hashed_password)


# Role-based access control
ROLE_PERMISSIONS = {
    "admin": [
        "manage_users",
        "manage_marinas",
        "approve_permits",
        "resolve_violations",
        "view_all_data",
        "modify_compliance_rules",
        "system_configuration"
    ],
    "marina_manager": [
        "approve_permits",
        "resolve_violations",
        "view_marina_data",
        "manage_berths",
        "manage_marina_staff"
    ],
    "staff": [
        "view_marina_data",
        "request_permits",
        "view_violations",
        "update_vessel_info"
    ],
    "user": [
        "view_own_data",
        "request_permits",
        "view_vessel_status"
    ]
}


def check_permission(role: str, permission: str) -> bool:
    """
    Check if role has permission

    Args:
        role: User role
        permission: Required permission

    Returns:
        True if role has permission
    """
    return permission in ROLE_PERMISSIONS.get(role, [])


def require_role(required_role: str):
    """
    Decorator to require specific role

    Usage:
        @require_role("marina_manager")
        async def approve_permit(user, permit_id):
            ...
    """
    def decorator(func):
        async def wrapper(user, *args, **kwargs):
            user_role = user.get("role")

            # Admin has all permissions
            if user_role == "admin":
                return await func(user, *args, **kwargs)

            # Check if user has required role
            role_hierarchy = ["admin", "marina_manager", "staff", "user"]
            if role_hierarchy.index(user_role) <= role_hierarchy.index(required_role):
                return await func(user, *args, **kwargs)

            raise PermissionError(f"Role '{user_role}' does not have permission to access this resource")

        return wrapper
    return decorator


# Example usage in FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    '''Get current authenticated user from JWT token'''
    token = credentials.credentials
    user = JWTHandler.get_user_from_token(token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@app.post("/api/v1/auth/login")
async def login(email: str, password: str):
    '''Login endpoint'''
    # Verify credentials (check database)
    user = get_user_by_email(email)

    if not user or not PasswordHandler.verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create tokens
    access_token = JWTHandler.create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        marina_id=user.marina_id
    )

    refresh_token = JWTHandler.create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "marina_id": user.marina_id
        }
    }


@app.post("/api/v1/verify/permit/approve")
async def approve_permit(
    permit_id: str,
    user: Dict = Depends(get_current_user)
):
    '''Approve hot work permit (requires marina_manager or admin role)'''
    if not check_permission(user["role"], "approve_permits"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to approve permits"
        )

    # Approve permit logic
    ...
"""
