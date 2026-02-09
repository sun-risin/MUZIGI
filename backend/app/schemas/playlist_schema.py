from marshmallow import Schema, fields

class TrackInfoSchema(Schema):
    title = fields.String(required=True)
    artist = fields.String(required=True)
    trackId = fields.String(required=True)
    
class PlaylistSchema(Schema):
    emotionName = fields.String(required=True)
    playlistId = fields.String(required=True)
    tracks = fields.Dict(
        keys=fields.String(),       # position (문자열)
        values=fields.Nested(TrackInfoSchema)    # trackInfo 객체
    )
    
# class PlaylistHistorySchema(Schema):
#     historyDocId = fields.String(required=True)
#     playlistId = fields.String(required=True)
#     tracks = fields.Dict(
#         keys=fields.String(),       # position (문자열)
#         values=fields.Nested(TrackInfoSchema)    # trackInfo 객체
#     )