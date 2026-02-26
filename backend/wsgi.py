# entry point
from app import create_app

app = create_app()

# Gunicorn으로 실행할 때는 이 부분 실행 X (Gunicorn이 'app' 객체 임포트)
if __name__ == '__main__':
    app.run(port=5002)