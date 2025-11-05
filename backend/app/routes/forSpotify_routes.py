import os
import base64
from dotenv import load_dotenv
import string
import random
import requests
from flask import Blueprint, redirect, request, session, jsonify
from firebase_admin import firestore

track_blp = Blueprint("track", __name__, url_prefix="/api/spotify")
db = firestore.client()


# .env 파일에서 환경 변수 로드
load_dotenv()
# 환경 변수에서 값 읽기
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
#리다이렉트할 프론트 위치는 /chat임
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5173/chat')
PORT = int(os.getenv('PORT', 5000))
BACKEND_CALLBACK_URL = os.getenv('BACKEND_CALLBACK_URL', f"http://127.0.0.1:{PORT}/api/spotify/auth/callback")
REDIRECT_URI = BACKEND_CALLBACK_URL

# 사용할 Spotify API 엔드포인트
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# 스포티파이 로그인 페이지로 리다이렉트할 때의 scope => 권한 설정
SCOPE = "streaming user-read-email user-read-private"

# 무작위 state 값을 생성하는 헬퍼 함수
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# 사용자를 Spotify 로그인 페이지로 보냄(리디렉션)
# 승인 코드를 받아 사용자 승인 요청.
@track_blp.route("/auth/login", methods=["GET"])
def spotify_login():
    state = generate_random_string(16)
    session['spotify_state'] = state
    
    auth_params = {
        'response_type': 'code',
        'client_id': SPOTIFY_CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI,
        'state': state
    }
    
    req = requests.models.PreparedRequest()
    req.prepare_url(SPOTIFY_AUTH_URL, params=auth_params)
    
    # Spotify 로그인 페이지로 리디렉션
    return redirect(req.url)


# Spotify에서 받은 정보로 토큰을 세션에 저장, 본 페이지로 리디렉션
# 이전 단계에서 요청한 승인 코드 사용해 액세스 토큰 요청
@track_blp.route("/auth/callback", methods=["GET"])
def spotify_callback():
    """
    /auth/callback 엔드포인트:
    1. Spotify에서 'code'와 'state'를 받음
    2. 'code'를 'access_token'으로 교환
    3. 토큰을 세션에 저장
    4. 사용자를 React 앱(프론트엔드)으로 리디렉션
    """
    
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = session.pop('spotify_state', None)
    
    if state is None or state != stored_state:
        return jsonify({"error": "State mismatch"}), 400

    # Access Token 요청
    auth_header_val = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_header = base64.b64encode(auth_header_val.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    try:
        response = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        
        token_data = response.json()
        
        # 토큰을 세션에 저장
        session['spotify_access_token'] = token_data.get('access_token')
        session['spotify_refresh_token'] = token_data.get('refresh_token')
        
        # --- React 앱의 메인 페이지로 리디렉션 ---
        return redirect(FRONTEND_URL) 
        # return redirect("/") # 테스트페이지

    except requests.exceptions.HTTPError as e:
        return jsonify({"error": "Failed to retrieve token", "details": str(e)}), 500
    
# 테스트 위해서 HTML에서 로그인 상태 확인할 수 있도록 작성한 토큰 반환하는 API
@track_blp.route("/auth/token", methods=["GET"])
def get_spotify_token():
    """
    /auth/token:
    HTML(클라이언트)가 현재 로그인 상태를 확인할 수 있도록
    세션에 저장된 토큰을 JSON으로 반환
    """
    access_token = session.get('spotify_access_token')
    
    if access_token:
        print("Returning token to client.")
        return jsonify({
            "access_token": access_token
        })
    else:
        print("No token found in session.")
        return jsonify({
            "error": "Not logged in"
        }), 401