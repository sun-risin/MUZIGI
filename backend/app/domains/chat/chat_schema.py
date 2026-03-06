from marshmallow import Schema, fields, EXCLUDE

class ChatSchema(Schema):
    chatId = fields.String(required=True)
    userDocId = fields.String(required=True)
    
    class Meta:
        unknown = EXCLUDE