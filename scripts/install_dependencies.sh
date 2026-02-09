#!/bin/bash
set -euo pipefail

APP_DIR="/home/ubuntu/muzigi"
VENV_DIR="${APP_DIR}/backend/venv"

echo "[AfterInstall] CodeDeploy가 파일 복사 완료 -> 설치 단계 시작... : to ${APP_DIR}"
cd "${APP_DIR}"


# .env 존재 여부 확인
if [ ! -f "${APP_DIR}/.env" ]; then
    echo "[ERROR] .env 파일이 존재하지 않습니다"
    exit 1
fi

# .env 로부터 환경변수 로드하기
echo "[AfterInstall] .env 환경변수 로드"
set -o allexport
source "${APP_DIR}/.env"
set +o allexport

# FIREBASE_CREDENTIALS_B64 검증
if [ -z "${FIREBASE_CREDENTIALS_B64}" ]; then
    echo "[ERROR] FIREBASE_CREDENTIALS_B64 값이 비어 있습니다!"
    exit 1
fi

echo "[AfterInstall] FIREBASE_CREDENTIALS_B64 -> JSON 디코딩"

# firebase 폴더 생성
mkdir -p "${APP_DIR}/firebase"
# Base64 → JSON 디코딩
echo "$FIREBASE_CREDENTIALS_B64" | base64 --decode > "${APP_DIR}/firebase/serviceAccountKey.json"
# 보안 위해 권한 수정
chmod 600 "${APP_DIR}/firebase/serviceAccountKey.json"

echo "[AfterInstall] Firebase 서비스 키 생성 완료"


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
