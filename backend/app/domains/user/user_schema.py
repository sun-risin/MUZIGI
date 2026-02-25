from marshmallow import Schema, fields, validate

class RegisterUserSchema(Schema):
    userId = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    nickname = fields.String(required=True, validate=validate.Length(min=1))

class UserSchema(Schema):
    userId = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    nickname = fields.String(required=True, validate=validate.Length(min=1))
    userDocId = fields.String(required=True)
    
    chatIds = fields.List(fields.String(required=True), required=True) # 채팅 아이디들
    
    playlistIds = fields.Dict( # 감정별 재생목록 아이디
        keys=fields.String(), values=fields.String(), required=True)