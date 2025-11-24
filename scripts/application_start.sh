#!/bin/bash
set -euo pipefail

APP_DIR="/home/ubuntu/muzigi"
SERVICE_NAME="muzigi"

echo "[ApplicationStart] systemd 데몬 reload 및 서비스 시작..."

# systemd unit 파일을 읽도록 강제 갱신
sudo systemctl daemon-reload

# 부팅 시 자동 시작 등록
sudo systemctl enable ${SERVICE_NAME}.service

# 서비스 재시작
sudo systemctl restart ${SERVICE_NAME}.service

# 상태 확인 (실패해도 배포 실패시키지 않도록 처리)
sleep 2 # Gunicorn이 안정적으로 뜰 때까지 약간 대기
echo "[ApplicationStart] Gunicorn 서비스 상태 확인"
if ! sudo systemctl status ${SERVICE_NAME}.service --no-pager; then
    echo "[WARNING] Gunicorn 서비스 상태 출력 중 오류 발생 (서비스 자체는 실행 중일 수 있음)"
fi

# nginx 설정 파일 복사
echo "[ApplicationStart] Nginx 설정 적용..."
sudo cp $APP_DIR/nginx/flask-app.conf /etc/nginx/sites-available/flask-app.conf

# 심볼릭 링크 생성(이미 있어도 덮어쓰기)
sudo ln -sf /etc/nginx/sites-available/flask-app.conf /etc/nginx/sites-enabled/flask-app.conf

# nginx 설정 테스트
sudo nginx -t

# nginx 재시작
sudo systemctl restart nginx

echo "[ApplicationStart] 모든 서비스가 성공적으로 시작되었습니다!"
