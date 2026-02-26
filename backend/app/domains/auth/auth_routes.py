from flask import Blueprint, request, jsonify, current_app

from auth_services import register_user, get_token_and_user_info

from app.common.apiResponse import ApiResponse

from functools import wraps
from jwt import ExpiredSignatureError, InvalidTokenError

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

    
# 로그인 유지 확인 데코레이터 함수 
def login_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        userToken = request.headers.get("Authorization")
        # 유저 토큰 없음
        if not userToken:
            return jsonify({"message": "토큰이 없습니다."}), 401

        # 나중에 유효기간 추가할 수도 있으니 포함해서 로직 구현
        try:
            # 토큰 디코딩 -> payload
            payload = jwt.decode(userToken, current_app.config['MUZIGI_JWT_KEY'], algorithms=['HS256'])
            userDocId = payload["userDocId"]
            user_doc = db.collection("users").document(userDocId).get()
            
            if not user_doc.exists: 
                return jsonify({"message": "유효하지 않은 사용자입니다."}), 401
            
            curr_user = user_doc.to_dict()
            
        except ExpiredSignatureError: # 유효기간 다 된 경우, 나중에 exp로 추가 가능
            return jsonify({"message": "토큰 만료"}), 401
        except InvalidTokenError:     # 토큰 값이 이상할 경우
            return jsonify({"message": "유효하지 않은 사용자 토큰"}), 401
        
        return func(curr_user, *args, **kwargs)
    
    return decorated_func

@auth_blp.route("/tokentest", methods=["GET"])
@login_required
def login_check(curr_user):
    return jsonify({
        "message": f"{curr_user['nickname']} 님, 인증 성공!"
    }), 200