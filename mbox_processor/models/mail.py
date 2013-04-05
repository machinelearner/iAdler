from mongoengine import *
import datetime

class Mail(EmbeddedDocument):
    from_user = StringField()
    from_email = StringField()
    to = ListField(StringField(),default=list)
    cc = ListField(StringField(),default=list)
    message_id = StringField(max_length=200, required=True)
    date = DateTimeField(default=datetime.datetime.now)
    body = StringField()
    subject = StringField()
