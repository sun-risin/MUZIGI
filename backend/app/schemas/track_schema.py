import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import firestore, credentials, initialize_app

# Firebase 초기화 (중복 실행 에러 방지)
if not firebase_admin._apps:
    cred = credentials.Certificate("../../../firebase/serviceAccountKey.json")
    initialize_app(cred)

db = firestore.client()

# Kaggle에서 다운로드 받은 csv 불러옴
Track_CSV_PATH = "C:/Users/user/Spotify_track.csv"
Track_df = pd.read_csv(Track_CSV_PATH)

Track_df = Track_df.rename(columns={"Unnamed: 0": "trackDocPos"}) # 첫 번째 열이 넘버링이었음. id로 쓰기 위해서 이름 바꿈
Track_df = Track_df[['trackDocPos', 'song_title', 'artist', 'danceability', 'energy', 'valence']] # 넘버링, 제목, 가수, 고유 음악 특성 3가지만 남김

COLLECTION_NAME = "Track" # Firestore 컬렉션 이름
batch = db.batch()
count = 0

print(f"'{Track_CSV_PATH}' 파일 읽기 완료. 총 {len(Track_df)}개의 행을 '{COLLECTION_NAME}' 컬렉션에 업로드 시작합니다.")

# DataFrame의 각 행 순회 / 'Track_df.iterrows()': (인덱스, 행(Series)) 튜플 반환
for index, row in Track_df.iterrows():

    doc_data = row.to_dict() # csv 행 데이터 => Firestore 문서의 데이터 (딕셔너리 형태로 넣어야 됨)

    # 문서 ID 지정
    doc_id = str(row['trackDocPos']) # 문서 위치(넘버링)로 문서 ID 사용
    doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
    
    # Firestore 필드에 ID가 중복 저장되지 않게 딕셔너리에서 문서 ID로 썼던 행 지움
    doc_data_without_id = row.drop('trackDocPos').to_dict() 
    batch.set(doc_ref, doc_data_without_id)
    
    count += 1
    
    # Firestore는 배치(batch) 쓰기 시 500개 제한 有, 500개마다 한 번씩 커밋(전송)!
    if count % 500 == 0:
        print(f"{count}개 행 배치 쓰기 중...")
        batch.commit()
        batch = db.batch() # 새 배치 시작

# 남은 데이터가 있다면 마지막으로 커밋
if count % 500 != 0:
    print(f"마지막 배치({count % 500}개) 쓰기 중...")
    batch.commit()

print(f"총 {count}개의 문서 업로드 완료!")