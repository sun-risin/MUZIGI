from marshmallow import Schema, fields
from track.track_schema import TrackInfoSchema
    
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