# 외부 라이브러리 초기화 모음 파일

import firebase_admin
from firebase_admin import credentials, initialize_app, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import os

# Firebase 초기화 및 Firestore 전역 객체 생성
db = None
def init_firestore(app):
    global db
    
    if not firebase_admin._apps:
        cred_path = "/home/ubuntu/muzigi/firebase/serviceAccountKey.json"

        if not os.path.exists(cred_path):
            raise RuntimeError(f"Firebase credential file not found: {cred_path}")

        cred = credentials.Certificate(cred_path)
        initialize_app(cred)
        
    db = firestore.client()