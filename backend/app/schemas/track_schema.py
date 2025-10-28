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

Track_df = Track_df[['track_id', 'track_name', 'track_artist', 
                     'danceability', 'energy', 'valence', 'track_popularity']]

# 중복, NULL 값 처리, 인덱스 재정립
Track_df = Track_df.drop_duplicates().dropna().reset_index(drop=True)

# COLLECTION_NAME = "Tracks" # Firestore 컬렉션 이름
batch = db.batch()
count = 0

# 데이터 내 한국 아티스트 리스트
korean_artists = [
    "TWICE", "SHINee", "BTS", "f(x)", "BoA", "2NE1", "PSY",
    "GOT7", "Red Velvet", "BLACKPINK", "GFRIEND", "SEVENTEEN",
    "NCT 127", "Wanna One", "ITZY", "Stray Kids", "ATEEZ",
    "DREAMCATCHER", "TAEYEON", "(G)I-DLE", "CHUNG HA",
    "EVERGLOW", "Rain", "IZ*ONE", "4Minute", "SUNMI", "DEAN",
    "PENTAGON", "TAEMIN", "HyunA", "WINNER", "EXID", "MOMOLAND",
    "iKON", "CL", "SuperM", "Ailee"
]

# 1차 DataFrame: 한국 아티스트만, 인기 점수 열은 필요 없으니 제거
Track_df_kpop = Track_df[Track_df['track_artist'].isin(korean_artists)]
Track_df_kpop = Track_df_kpop.loc[:, Track_df_kpop.columns != 'track_popularity']

# 2차 DataFrame: 한국 아티스트 제외 인기 점수 55점 이상
Track_df_popular_foreign = Track_df[
    (~Track_df['track_artist'].isin(korean_artists)) &
    (Track_df['track_popularity'] >= 55)]
# 이제 인기 점수 필요 없음
Track_df_popular_foreign = Track_df_popular_foreign.loc[:, Track_df_popular_foreign.columns != 'track_popularity']

print(f"'{Track_CSV_PATH}' 파일 읽기 완료. Kpop 관련: {len(Track_df_kpop)}, 이외 인기 곡: {len(Track_df_popular_foreign)}")


# 한국 아티스트 내용 저장 컬렉션 - TracksKpop
# DataFrame의 각 행 순회 / 'Track_df_kpop.iterrows()': (인덱스, 행(Series)) 튜플 반환
for index, row in Track_df_kpop.iterrows():

    doc_data = row.to_dict() # csv 행 데이터 => Firestore 문서의 데이터 (딕셔너리 형태로 넣어야 됨)

    # 문서 ID 지정
    doc_id = str(row['track_id']) # spotify 제공 id
    doc_ref = db.collection("TracksKpop").document(doc_id)
    
    # Firestore 필드에 ID가 중복 저장되지 않게 딕셔너리에서 문서 ID로 썼던 행 지움
    doc_data_without_id = row.drop('track_id').to_dict() 
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

print(f"Kpop 곡들, 총 {count}개의 문서 TracksKpop에 업로드 완료!")

count = 0 # 다시 0개

# 이외 인기곡 저장 컬렉션 - TracksPopular
for index, row in Track_df_popular_foreign.iterrows():

    doc_data = row.to_dict() # csv 행 데이터 => Firestore 문서의 데이터 (딕셔너리 형태로 넣어야 됨)

    # 문서 ID 지정
    doc_id = str(row['track_id']) # spotify 제공 id
    doc_ref = db.collection("TracksPopular").document(doc_id)
    
    # Firestore 필드에 ID가 중복 저장되지 않게 딕셔너리에서 문서 ID로 썼던 행 지움
    doc_data_without_id = row.drop('track_id').to_dict() 
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

print(f"해외 인기곡들, 총 {count}개의 문서 TracksPopular에 업로드 완료!")