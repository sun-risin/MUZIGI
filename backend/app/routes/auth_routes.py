from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from werkzeug.security import generate_password_hash, check_password_hash
from app.schemas.user_schema import UserSchema

auth_blp = Blueprint("auth", __name__, url_prefix="/auth")
db = firestore.client()
user_schema = UserSchema()

# 회원가입
@auth_blp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    errors = user_schema.validate(data) # schema로 유효성 검사
    if errors:
        return jsonify({
        "error": errors,
        "message": "유효하지 않은 입력값입니다."
    }), 400

    userId = data["userId"]
    password = data["password"]
    nickname = data["nickname"]

    # 아이디 중복 체크
    user_ref = db.collection("users").where("userId", "==", userId).stream()
    if any(user_ref):
        return jsonify({"error": "이미 존재하는 아이디입니다."}), 409

    # 비밀번호 해싱 후 저장 예정
    hashed_pw = generate_password_hash(password)

    # Firestore에 저장
    db.collection("users").add({
        "userId": userId,
        "password": hashed_pw,
        "nickname": nickname,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    return jsonify({"message": "회원가입 성공"}), 201


# 로그인 + 토큰 발급하여 서비스 로그인 유지