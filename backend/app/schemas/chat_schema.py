from marshmallow import Schema, fields

class ChatSchema(Schema):
    chatId = fields.String()
    userDocId = fields.String()