from marshmallow import Schema, fields, validate

class EmotionCategorySchema(Schema):
    emotionName = fields.String()
    empathyMent = fields.String()
    trackTraits = fields.String()