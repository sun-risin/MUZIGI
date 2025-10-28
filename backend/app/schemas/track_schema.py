"""
이 파일은 marshmallow schema 관련 파일이 아닌,
firestore에 kaggle의 csv 파일 데이터를 업로드하는 것에 대한 로직 파일입니다.
csv 파일에서 원하는 부분만 고르고 열 이름을 변경한 후, 컬렉션 이름과 문서 ID를 지정하여 저장하였습니다.
"""

import pandas as pd
import firebase_admin
from firebase_admin import firestore, credentials, initialize_app

# Firebase 초기화 (중복 실행 에러 방지)
if not firebase_admin._apps:
    cred = credentials.Certificate("../firebase/serviceAccountKey.json")
    initialize_app(cred)

db = firestore.client()

# Kaggle에서 다운로드 받은 csv 불러옴
Track_CSV_PATH = "C:/Users/user/spotify_songs.csv"
Track_df = pd.read_csv(Track_CSV_PATH)

Track_df = Track_df[['track_id', 'track_name', 'track_artist', 'danceability', 'energy', 'valence']]

# 중복, NULL 값 처리
Track_df = Track_df.drop_duplicates()
Track_df = Track_df.dropna()

COLLECTION_NAME = "Tracks" # Firestore 컬렉션 이름
batch = db.batch()
count = 0

start_index = 19500  # 어제 저장 중단된 지점

print(f"'{Track_CSV_PATH}' 파일 읽기 완료. 총 {len(Track_df)}개의 행을 '{COLLECTION_NAME}' 컬렉션에 업로드 시작합니다.")


# 19500인덱스부터 나머지 재업로드
for i in range(start_index, len(Track_df)):
    row = Track_df.iloc[i]
    
    doc_data = row.to_dict() 
    doc_id = str(row['track_id'])
    doc_ref = db.collection(COLLECTION_NAME).document(doc_id)

    doc_data_without_id = row.drop('track_id').to_dict() 
    batch.set(doc_ref, doc_data_without_id)
    
    if (i+1) % 500 == 0:
        print(f"{count}개 행 배치 쓰기...")
        batch.commit()
        batch = db.batch()

if (i+1) % 500 != 0:
    print(f"마지막 배치({len(Track_df) - (i//500)*500}개) 쓰기 중...")
    batch.commit()

print(f"총 {len(Track_df) - start_index}개의 문서 업로드 완료 (인덱스 {start_index}~{len(Track_df)-1})")


# # DataFrame의 각 행 순회 / 'Track_df.iterrows()': (인덱스, 행(Series)) 튜플 반환
# for index, row in Track_df.iterrows():

#     doc_data = row.to_dict() # csv 행 데이터 => Firestore 문서의 데이터 (딕셔너리 형태로 넣어야 됨)

#     # 문서 ID 지정
#     doc_id = str(row['track_id']) # spotify 제공 id
#     doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
    
#     # Firestore 필드에 ID가 중복 저장되지 않게 딕셔너리에서 문서 ID로 썼던 행 지움
#     doc_data_without_id = row.drop('track_id').to_dict() 
#     batch.set(doc_ref, doc_data_without_id)
    
#     count += 1
    
#     # Firestore는 배치(batch) 쓰기 시 500개 제한 有, 500개마다 한 번씩 커밋(전송)!
#     if count % 500 == 0:
#         print(f"{count}개 행 배치 쓰기 중...")
#         batch.commit()
#         batch = db.batch() # 새 배치 시작

# # 남은 데이터가 있다면 마지막으로 커밋
# if count % 500 != 0:
#     print(f"마지막 배치({count % 500}개) 쓰기 중...")
#     batch.commit()

# print(f"총 {count}개의 문서 업로드 완료!")