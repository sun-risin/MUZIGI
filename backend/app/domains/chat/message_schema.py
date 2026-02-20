from marshmallow import Schema, fields
from track.track_schema import TrackInfoSchema

class MessageSchema(Schema):
    chatId = fields.String()
    content = fields.String()
    messageId = fields.String()
    senderType = fields.Boolean()
    senderId = fields.String()
    emotionName = fields.String()
    recommendTracks = fields.List(fields.Dict(
        keys= fields.String(),
        values=fields.Nested(TrackInfoSchema)
    ))
    created_at = fields.DateTime()