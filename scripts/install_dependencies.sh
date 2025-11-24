#!/bin/bash
set -euo pipefail

APP_DIR="/home/ubuntu/muzigi"
VENV_DIR="${APP_DIR}/backend/venv"

echo "[AfterInstall] CodeDeploy가 파일 복사 완료 -> 설치 단계 시작 : to ${APP_DIR}"
cd "${APP_DIR}"

# GitHub Secrets에 저장된 Firebase Base64 문자열이 존재하면 JSON으로 복원
if [ -n "$FIREBASE_CREDENTIALS_B64" ]; then
  echo "[AfterInstall] FIREBASE_CREDENTIALS_B64 값을 JSON으로 디코딩합니다"
  
  mkdir -p "${APP_DIR}/firebase"
  echo "$FIREBASE_CREDENTIALS_B64" | base64 --decode > "${APP_DIR}/firebase/serviceAccountKey.json"
  
  # 권한을 600으로 제한 (보안 목적)
  chmod 600 "${APP_DIR}/firebase/serviceAccountKey.json"
fi

# create/refresh virtualenv
echo "[AfterInstall] 새 Python 가상환경 생성..."
python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

# requirements.txt 있으면 설치
echo "[AfterInstall] pip 업그레이드 및 requirements.txt 설치..."
python -m pip install --upgrade pip
if [ -f "${APP_DIR}/backend/requirements.txt" ]; then
  pip install -r "${APP_DIR}/backend/requirements.txt"
else
  echo "[AfterInstall] requirements.txt 없음 — 설치 스킵"
fi
