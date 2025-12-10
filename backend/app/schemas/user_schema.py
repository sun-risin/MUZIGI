from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    userId = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    nickname = fields.String(required=True, validate=validate.Length(min=1))
    userDocId = fields.String()
    chatIds = fields.List(fields.String())
    playlistIds = fields.List(fields.String())
    userDocId = fields.String()