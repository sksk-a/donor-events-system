class AppError(Exception):
    """Base application exception safe to display to a user."""


class EntityNotFoundError(AppError):
    pass


class BusinessRuleError(AppError):
    pass


class DatabaseError(AppError):
    pass


class ValidationError(AppError):
    pass
