"""Custom exceptions for Ada Maritime AI"""


class AdaException(Exception):
    """Base exception for Ada Maritime AI"""
    pass


class ConfigurationError(AdaException):
    """Configuration error"""
    pass


class DatabaseError(AdaException):
    """Database operation error"""
    pass


class SkillExecutionError(AdaException):
    """Skill execution error"""
    pass


class ValidationError(AdaException):
    """Data validation error"""
    pass


class BerthNotFoundError(DatabaseError):
    """Berth not found"""
    pass


class BerthNotAvailableError(DatabaseError):
    """Berth is not available"""
    pass


class BookingError(DatabaseError):
    """Booking operation error"""
    pass


class OrchestratorError(AdaException):
    """Orchestrator error"""
    pass
