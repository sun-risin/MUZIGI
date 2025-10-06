from flask import Flask
import firebase_admin
from firebase_admin import credentials, initialize_app

def create_app():
    app = Flask(__name__)
    
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