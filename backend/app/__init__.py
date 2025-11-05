import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, initialize_app

def create_app():
    # .env 파일에서 환경 변수 로드
    load_dotenv()
    
    # Flask 앱 설정
    app = Flask(__name__)
    
    # 세션 사용을 위한 Secret Key 설정
    app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))
    
    # 환경 변수에서 값 읽기
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    # CORS 허용 위해 프론트엔드 URL - 배포 생각해서 지정하는 식으로 수정함
    FRONTEND_URL = os.getenv("FRONTEND_URL", 'http://localhost:5173')
    
    # JWT 인증 비밀키 설정
    app.config['MUZIGI_JWT_KEY'] = 'muzigi-secret'
    
    # 리액트 Vite 서버 요청 허용
    # + supports_credentials=True -> 세션 쿠키 주고받게.
    CORS(app,
         resources={r"/*": {"origins": FRONTEND_URL}}, supports_credentials=True)
    
    # Firebase 초기화 (중복 실행 에러 방지)
    if not firebase_admin._apps:
        cred = credentials.Certificate("../firebase/serviceAccountKey.json")
        initialize_app(cred)

    # --- Blueprint 등록 ---    
    from app.routes import main_route, auth_routes, chat_routes, forSpotify_routes
       
    # 테스트 페이지 렌더링
    app.register_blueprint(main_route.main_blp)
    
    # auth_routes
    app.register_blueprint(auth_routes.auth_blp)
    
    #chat_routes
    app.register_blueprint(chat_routes.chat_blp)
    
    #forSpotify_routes
    app.register_blueprint(forSpotify_routes.track_blp)
    
    return app