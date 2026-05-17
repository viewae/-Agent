class AppException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, message=message)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(status_code=422, message=message)


class RateLimitError(AppException):
    def __init__(self, message: str = "Too many requests"):
        super().__init__(status_code=429, message=message)


class LLMTimeoutError(AppException):
    def __init__(self, message: str = "LLM request timed out"):
        super().__init__(status_code=504, message=message)


class LLMTokenLimitError(AppException):
    def __init__(self, message: str = "Context too long"):
        super().__init__(status_code=413, message=message)


class TaskNotFoundError(AppException):
    def __init__(self, message: str = "Task not found"):
        super().__init__(status_code=404, message=message)
