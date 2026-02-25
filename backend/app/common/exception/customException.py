# custom exception class -> errorcode와 함께 raise할 예외

from errorCode import ErrorCode

class CustomException(Exception):
    def __init__(self, error_code: ErrorCode):
        self.error_code = error_code