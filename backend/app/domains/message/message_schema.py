from marshmallow import Schema, fields, EXCLUDE
from ..track.track_schema import TrackInfoSchema

class MessageSchema(Schema):
    chatId = fields.String()
    content = fields.String()
    messageId = fields.String()
    senderType = fields.Boolean()
    senderId = fields.String()
    emotionName = fields.String()
    recommendTracks = fields.List(fields.Nested(TrackInfoSchema))
    
    class Meta:
        unknown = EXCLUDE