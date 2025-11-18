class AppError(Exception):
    """Базовый класс для всех ошибок приложения."""
    pass

class ParsingError(AppError):
    """Возникает, когда сервис парсинга не может обработать SQL."""
    pass

class ValidationError(AppError):
    """Возникает, когда сервис валидации находит нарушение."""
    pass

class TransformationError(AppError):
    """Возникает, когда сервис трансформации не может изменить AST."""
    pass