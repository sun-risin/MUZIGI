from flask import Flask
import firebase_admin
from firebase_admin import credentials, initialize_app

def create_app():
    app = Flask(__name__)
    # TODO: React 서버의 요청 허용하는 CORS 코드 (나중에 배포 시 도메인 추가)
    
    # Firebase 초기화 (중복 실행 에러 방지)
    if not firebase_admin._apps:
        cred = credentials.Certificate("../firebase/serviceAccountKey.json")
        initialize_app(cred)

    # --- Blueprint 등록 ---    
    # auth_routes
    from app.routes import main_routes, auth_routes
    app.register_blueprint(main_routes.main_blp)
    app.register_blueprint(auth_routes.auth_blp)

    return app