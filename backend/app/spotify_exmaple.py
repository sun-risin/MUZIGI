import os
import base64
import requests
import string
import random
from flask import Flask, redirect, request, session, url_for, jsonify
from dotenv import load_dotenv
from flask_cors import CORS  # CORS 임포트

# .env 파일에서 환경 변수 로드
load_dotenv()

# Flask 앱 설정 (정적 파일 관련 설정 제거)
app = Flask(__name__)

# 세션을 사용하기 위해 Secret Key가 필요합니다.
# (os.urandom(24)은 서버가 재시작될 때마다 키가 바뀌므로,
#  배포 시에는 고정된 문자열을 .env에 넣고 os.getenv('FLASK_SECRET_KEY')로 로드하는 것이 좋습니다.)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# 환경 변수에서 값 읽기
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5173') # React 앱 주소

# --- CORS 설정 ---
# React 앱(FRONTEND_URL)에서의 API 요청을 허용합니다.
# supports_credentials=True는 세션 쿠키를 주고받기 위해 필요합니다.
CORS(app, 
     resources={r"/auth/*": {"origins": FRONTEND_URL}}, 
     supports_credentials=True)

# Spotify API 엔드포인트
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# 서버 포트 및 리디렉션 URI
PORT = int(os.getenv('PORT', 5000))

# REDIRECT_URI도 환경 변수(배포 시)를 우선 사용하고, 없으면 개발용 주소를 사용합니다.
# 예: 배포 시 https://api.yourdomain.com/auth/callback
BACKEND_CALLBACK_URL = os.getenv('BACKEND_CALLBACK_URL', f"http://127.0.0.1:{PORT}/auth/callback")
REDIRECT_URI = BACKEND_CALLBACK_URL
SCOPE = "streaming user-read-email user-read-private"

# state 값을 생성하는 헬퍼 함수
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/auth/login')
def login():
    """
    /auth/login 엔드포인트:
    사용자를 Spotify 권한 부여 페이지로 리디렉션
    """
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

@app.route('/auth/callback')
def callback():
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
        
        # --- 중요: React 앱의 메인 페이지로 리디렉션 ---
        return redirect(FRONTEND_URL) 

    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Failed to retrieve token", "details": str(err)}), 500

# --- React 정적 파일 제공 로직 (모두 제거됨) ---
# @app.route('/')
# @app.route('/<path:path>')
# ... (삭제) ...

# 이 블록은 'python app.py'로 직접 실행할 때만 사용됩니다.
# Gunicorn으로 실행할 때는 이 부분이 실행되지 않습니다. (Gunicorn이 'app' 객체를 임포트함)
if __name__ == '__main__':
    print(f"--- Spotify 대시보드에 다음 Redirect URI를 추가하세요 ---")
    print(f"-> {REDIRECT_URI}")
    print("---------------------------------------------------------")
    print(f"Flask API 서버가 http://127.0.0.1:{PORT} 에서 실행 중입니다...")
    print(f"React 앱(CORS 허용): {FRONTEND_URL}")
    app.run(port=PORT, debug=True)
    
    
    
"""
코드 주요 포인트 (Node.js vs Flask)

서버 및 환경변수:
Express -> Flask
    dotenv.config() -> load_dotenv()
    process.env.VAR -> os.getenv('VAR')

/auth/login (로그인 시작):
    목적: 사용자를 Spotify 로그인 페이지로 보낸다.
    Node.js: URL 문자열을 직접 만들고 res.redirect()를 사용합니다.
    Flask: 
        requests.models.PreparedRequest를 사용해 
        URL 파라미터를 안전하게 인코딩하고 redirect() 함수를 사용합니다.
    State (CSRF 방지): 
        Node.js 예제에서는 문자열 생성을 제안만 했지만,
        Flask 예제에서는 random 모듈로 state를 생성하고 session에 저장하여
        /auth/callback에서 검증하는 로직을 포함했습니다. 
        (Flask의 session을 사용하려면 app.secret_key 설정이 필수입니다.)

/auth/callback (토큰 교환):
    목적: Spotify가 리디렉션할 때 보내주는 code를 access_token으로 교환한다.
    Node.js: request 패키지를 사용해 POST 요청을 보냅니다.
    Flask: requests 라이브러리의 requests.post()를 사용합니다.
    Authorization 헤더: 
        Basic <base64(id:secret)>을 만드는 로직은 동일합니다.
        Flask에서는 base64 모듈을 사용합니다.
    토큰 저장: 
        Node.js 예제는 "로컬에 저장"이라고 언급했지만, Flask 예제에서는
        웹 애플리케이션에서 일반적인 방식인 session에 토큰을 저장합니다.
    리디렉션: res.redirect('/') -> redirect(url_for('index'))
"""