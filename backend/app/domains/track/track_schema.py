from marshmallow import Schema, fields

class TrackInfoSchema(Schema):
    title = fields.String(required=True)
    artist = fields.String(required=True)
    trackId = fields.String(required=True)