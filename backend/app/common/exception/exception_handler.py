from ..apiResponse import ApiResponse
from .customException import CustomException
from requests.exceptions import HTTPError

def register_error_handlers(app):
    
    # custom exception 핸들링
    @app.errorhandler(CustomException)
    def handle_custom_error(e):
        return ApiResponse.error_byCode(e.error_code)
    
    # spotify api 관련 에러
    @app.errorhandler(HTTPError)
    def handle_spotify_error(e):
        return ApiResponse.error(
            status=500, message=f"spotify API 처리 중 오류 발생: {str(e)}")