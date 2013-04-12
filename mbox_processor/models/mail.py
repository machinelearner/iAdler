from mongoengine import *
import datetime
import re

class Mail(EmbeddedDocument):
    class Meta:
        app_label = 'mbox_processor'

    from_user = StringField()
    from_email = StringField()
    to = ListField(StringField(),default=list)
    cc = ListField(StringField(),default=list)
    message_id = StringField(max_length=200, required=True)
    date = DateTimeField(default=datetime.datetime.now)
    body = StringField()
    subject = StringField()

    def extract_user_name(self):
        if not self.from_user.strip():
            return self.from_email
        special_char_regex = re.compile("[\!=\?\\\]|(utf)",re.IGNORECASE)
        if special_char_regex.findall(self.from_user,):
            return self.from_email
        return self.from_user

