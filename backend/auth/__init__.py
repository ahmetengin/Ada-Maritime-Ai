"""
Authentication Module
JWT-based authentication and authorization for Ada Maritime AI
"""

from .jwt_handler import (
    JWTHandler,
    PasswordHandler,
    check_permission,
    require_role,
    ROLE_PERMISSIONS
)

__all__ = [
    "JWTHandler",
    "PasswordHandler",
    "check_permission",
    "require_role",
    "ROLE_PERMISSIONS"
]
