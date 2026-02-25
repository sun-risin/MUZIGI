from backend import app
from common.apiResponse import ApiResponse
from customException import CustomException

# custom exception 핸들링
@app.errorhandler(CustomException)
def handle_custom_error(e):
    return ApiResponse.error_byCode(e)