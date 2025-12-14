class AppError(Exception):
    pass

class ParsingError(AppError):
    pass

class ValidationError(AppError):
    pass

class TransformationError(AppError):
    pass