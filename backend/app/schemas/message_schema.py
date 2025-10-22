from marshmallow import Schema, fields

class MessageSchema(Schema):
    chatId = fields.String()
    content = fields.String()
    messageId = fields.String()
    senderType = fields.Boolean()
    senderId = fields.String()