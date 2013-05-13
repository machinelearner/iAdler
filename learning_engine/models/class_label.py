from mongoengine import *

class ClassLabel(Document):
    name  = StringField()

    class Meta:
        app_label = 'learning_engine'

