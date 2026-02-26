from flask import Blueprint, request

from auth_services import register_user, get_token_and_user_info
from app.common.apiResponse import ApiResponse
from decorater import login_required

auth_blp = Blueprint("auth", __name__, url_prefix="/api/auth")

# 회원가입
@auth_blp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    
    register_user(data) # 회원가입 서비스 로직

    return ApiResponse.success(
        status=201, message="회원가입 성공")


# JWT 인증 로그인
@auth_blp.route("/login", methods=["POST"])
def login():
    request_data = request.get_json()
    
    response_data = get_token_and_user_info(request_data)
    
    return ApiResponse.success(
        status=200, message="로그인 성공", data=response_data)


@auth_blp.route("/tokentest", methods=["GET"])
@login_required
def login_check(curr_user):
    return ApiResponse.success(
        status=200, 
        message=f"{curr_user['nickname']} 님, 인증 성공!")