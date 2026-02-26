# db 내 문서 ID와 매핑하기 위한 util 모음 파일

# firestore에서 emotionName으로 매핑될 문서 ID
kor_key = {
    "행복" : "happiness",
    "신남": "excited",
    "화남" : "aggro",
    "슬픔" : "sorrow",
    "긴장" : "nervous" }

eng_key = {val : key for key, val in kor_key.items()}

class EmotionMapping:
    
    @staticmethod
    def kor_to_eng(kor):
        return kor_key.get(kor, "wrong")
    
    @staticmethod
    def eng_to_kor(eng):
        return eng_key.get(eng, "wrong")