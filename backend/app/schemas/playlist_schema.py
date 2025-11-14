from marshmallow import Schema, fields

class PlaylistSchema(Schema):
    emotionName = fields.String()
    playlistId = fields.String()
    userDocId = fields.String()
    
class PlaylistHistorySchema(Schema):
    playlistId = fields.String()
    tracks = fields.List(fields.Mapping(fields.String()))
    # tracks -> 딕셔너리 배열. 각 인덱스에 가수, 제목, 음악 id 정보가 있다