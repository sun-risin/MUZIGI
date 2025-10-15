from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, initialize_app

def create_app():
    app = Flask(__name__)
    # 리액트 Vite 서버 요청 허용
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173/"]}}) # 나중에 배포 시 도메인 추가

    # Firebase 초기화 (중복 실행 에러 방지)
    if not firebase_admin._apps:
        cred = credentials.Certificate("../firebase/serviceAccountKey.json")
        initialize_app(cred)

    # --- Blueprint 등록 ---    
    # auth_routes
    from app.routes import main_route, auth_routes
    app.register_blueprint(main_route.main_blp)
    app.register_blueprint(auth_routes.auth_blp)
    return app