from marshmallow import Schema, fields

class PlaylistSchema(Schema):
    emotionName = fields.String()
    playlistId = fields.String()
    userDocId = fields.String()
    
class PlaylistHistorySchema(Schema):
    chatId = fields.String()
    content = fields.String()
    messageId = fields.String()
    senderType = fields.Boolean()
    senderId = fields.String()