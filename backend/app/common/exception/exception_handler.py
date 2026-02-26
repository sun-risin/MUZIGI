from ..apiResponse import ApiResponse
from .customException import CustomException

def register_error_handlers(app):
    # custom exception 핸들링
    @app.errorhandler(CustomException)
    def handle_custom_error(e):
        return ApiResponse.error_byCode(e.error_code)