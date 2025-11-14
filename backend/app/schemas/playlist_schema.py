from marshmallow import Schema, fields

class PlaylistSchema(Schema):
    emotionName = fields.String()
    playlistId = fields.String()
    userDocId = fields.String()
    
class PlaylistHistorySchema(Schema):
    playlistId = fields.String()
    tracks = fields.List(fields.Mapping(fields.String()))