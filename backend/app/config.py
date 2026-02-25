# 앱 설정값 모음 파일

import os
from dotenv import load_dotenv, find_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv(find_dotenv())

# --- 설정을 객체로 묶기 -> 변수들 app.config에 자동 등록됨
# 공통 설정
class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    MUZIGI_JWT_KEY = os.getenv("MUZIGI_JWT_KEY")
    CORS_SUPPORTS_CREDENTIALS = True # 세션 쿠키 주고받게.
    
# 환경별 설정
# 개발
class DevConfig(Config):
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")
    CORS_RESOURCES = {r"/*": {"origins": FRONTEND_URL}}
    DEBUG = True
    
# 배포
class ProdConfig(Config):
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://muzigi.vercel.app")
    CORS_RESOURCES = {r"/*": {"origins": FRONTEND_URL}}
    DEBUG = False
    
# 환경에 따라 설정 따라가게 함
config_by_env ={
    "dev" : DevConfig,
    "prod" : ProdConfig
}
def get_flask_env():
    env = os.getenv("FLASK_ENV", "dev")
    
    if env not in config_by_env: # 안전장치...
        raise RuntimeError(f"Invalid FLASK_ENV : {env}")