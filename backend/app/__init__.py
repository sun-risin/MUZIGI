from flask import Flask
from .config import get_flask_env, config_by_env
from flask_cors import CORS
from .extensions import init_firestore
from .common.exception.exception_handler import register_error_handlers

from .domains.auth import auth_routes
from .domains.chat import chat_routes
from .domains.spotify import forSpotify_routes
from .domains.playlist import playlist_routes

def create_app():    
    # Flask 앱 설정
    app = Flask(__name__)
    
    # --- config ---
    # 로드
    app.config.from_object(config_by_env[get_flask_env()])
    
    # 필수값 검증
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("FLASK_SECRET_KEY is not set")
    if not app.config["MUZIGI_JWT_KEY"]:
        raise RuntimeError("MUZIGI_JWT_KEY is not set")
    if not app.config["CORS_RESOURCES"]:
        raise RuntimeError("CORS_RESOURCES is not set")
    if not app.config["CORS_SUPPORTS_CREDENTIALS"]:
        raise RuntimeError("CORS_SUPPORTS_CREDENTIALS is not set")
    if not app.config["DB_CREDENTIAL_PATH"]:
        raise RuntimeError("DB_CREDENTIAL_PATH is not set")
    
    # CORS 적용   
    CORS(app,
         resources=app.config["CORS_RESOURCES"], 
         supports_credentials=app.config["CORS_SUPPORTS_CREDENTIALS"])
    
    # --- extension ---
    # DB
    init_firestore(app)
    
    # --- 에러 핸들러 ---
    register_error_handlers(app)
        
    # --- Blueprint 등록 ---        
    app.register_blueprint(auth_routes.auth_blp)            # auth_routes 
    app.register_blueprint(chat_routes.chat_blp)            # chat_routes
    app.register_blueprint(forSpotify_routes.track_blp)     # forSpotify_routes
    app.register_blueprint(playlist_routes.playlist_blp)    # playlist_routes
    
    return app