#!/bin/bash
set -euo pipefail

APP_DIR="/home/ubuntu/muzigi" # 앱 배포될 디렉토리
SERVICE_NAME="muzigi" # systemd 서비스 이름

echo "[BeforeInstall] 기존 서비스가 실행 중이면 종료..."

# systemd 서비스가 실행 중인지 확인
if sudo systemctl is-active --quiet ${SERVICE_NAME}.service; then
  # 실행중이면 중지
  sudo systemctl stop ${SERVICE_NAME}.service
  echo "[BeforeInstall] 기존 서비스 ${SERVICE_NAME} 종료 완료"
else
  echo "[BeforeInstall] 실행 중인 서비스 ${SERVICE_NAME} 없음"
fi

echo "[BeforeInstall] 기존 앱 디렉토리 삭제 후 재생성..."

# 이전 배포 버전 디렉토리 삭제
if [ -d "${APP_DIR}" ]; then
  sudo rm -rf "${APP_DIR}"
fi

# 새 디렉토리 생성 후 권한 ubuntu로 설정
mkdir -p "${APP_DIR}"
sudo chown ubuntu:ubuntu "${APP_DIR}"
