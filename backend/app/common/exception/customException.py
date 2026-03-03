# custom exception class -> errorcode와 함께 raise할 예외

from .errorCode import ErrorCode

class CustomException(Exception):
    def __init__(self, error_code: ErrorCode):
        super().__init__(error_code.message)
        self.error_code = error_code
        
class ValidateException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        
class UnknownException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        
class SpotifyNotFoundException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message