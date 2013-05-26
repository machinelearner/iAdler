from mongoengine import *

class User(Document):
    class Meta:
        app_label = 'mbox_processor'

    name = StringField()
    email = StringField()