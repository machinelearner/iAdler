from mongoengine import *

class ClassScore(EmbeddedDocument):
    label  = StringField()
    frequency  = FloatField()
    probability = FloatField()

    class Meta:
        app_label = 'learning_engine'


