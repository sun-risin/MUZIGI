#!/bin/bash
set -e

# Gunicorn 포트 체크
echo "[VALIDATE] 애플리케이션 실행되는지 확인"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5002)

if [ "$STATUS" -ne 200 ]; then
    echo "[VALIDATE] 애플리케이션이 시작하지 못했음(HTTP $STATUS)"
    exit 1
fi

echo "[VALIDATE] 애플리케이션이 잘 실행되고 있음"
