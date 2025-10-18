from marshmallow import Schema, fields

class EmotionCategorySchema(Schema):
    emotionName = fields.String()
    empathyMent = fields.List()
    trackTraits = fields.Mapping()
    
# 따로 코드로 추가하거나 할 일은 없기 때문에 일단은 이렇게만 작성
