from marshmallow import Schema, fields

class PlaylistSchema(Schema):
    emotionName = fields.String(required=True)
    playlistId = fields.String(required=True)
    userDocId = fields.String(required=True)
    
class PlaylistHistorySchema(Schema):
    playlistId = fields.String(required=True)
    tracks = fields.List(fields.Mapping(fields.String()), required=True)
    # tracks -> 딕셔너리 배열. 각 인덱스에 가수, 제목, 음악 id 정보가 있다