# entry point
import os
from dotenv import load_dotenv, find_dotenv
from app import create_app

app = create_app()

load_dotenv(find_dotenv())   # .env 파일에서 환경 변수 로드 -> Flask 실행위치 관계 없이 찾게 수정함

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5173')
PORT = int(os.getenv('PORT', 5000)) 

# REDIRECT_URI도 환경 변수를 우선 사용(배포 시), 없으면 개발용 주소 사용
#   예: 배포 시 https://api.mydomain.com/auth/callback
BACKEND_CALLBACK_URL = os.getenv('BACKEND_CALLBACK_URL', f"http://127.0.0.1:{PORT}/api/spotify/auth/callback")
REDIRECT_URI = BACKEND_CALLBACK_URL
    
# Gunicorn으로 실행할 때는 이 부분 실행 X (Gunicorn이 'app' 객체 임포트)
if __name__ == '__main__':
    print(f"--- Spotify 대시보드에 다음 Redirect URI를 추가하세요 ---")
    print(f"-> {REDIRECT_URI}")
    print("---------------------------------------------------------")
    print(f"Flask API 서버가 http://127.0.0.1:{PORT} 에서 실행 중입니다...")
    print(f"React 앱(CORS 허용): {FRONTEND_URL}")
    app.run(port=PORT, debug=True)