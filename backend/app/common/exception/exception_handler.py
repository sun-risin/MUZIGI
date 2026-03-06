from ..apiResponse import ApiResponse
from .customException import CustomException, ValidateException, UnknownException, ErrorCode, SpotifyNotFoundException
from requests.exceptions import HTTPError

def register_error_handlers(app):
    
    # 진짜 예상치 못한 버그... 에러 핸들링
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return ApiResponse.error(status=500, message=str(e))
    
    # custom exception 핸들링
    @app.errorhandler(CustomException)
    def handle_custom_error(e):
        return ApiResponse.error_byCode(e.error_code)
    
    # 사용자 입력 validate 에러 (400)
    @app.errorhandler(ValidateException)
    def handle_validate_error(e):
        return ApiResponse.error(
            status=400, message=e.message)
    
    # 알 수 없는 에러 처리 (500)
    @app.errorhandler(UnknownException)
    def handle_unknown_error(e):
        return ApiResponse.error(
            status=500, message=e.message)
    
    # spotify api 관련 에러
    @app.errorhandler(HTTPError)
    def handle_spotify_error(e):
        return ApiResponse.error(
            status=e.response.status_code if e.response else 500,
            message=f"spotify API 처리 중 오류 발생: {str(e)}")
        
    @app.errorhandler(SpotifyNotFoundException)
    def handle_spotify_notfound_error(e):
        return ApiResponse.error(
            status=404, message=e.message)