from mongoengine import *
from mbox_processor.models import User
import datetime
import re

class Mail(EmbeddedDocument):
    class Meta:
        app_label = 'mbox_processor'

    sender = ReferenceField(User,required=True)
    to = ListField(StringField(),default=list)
    cc = ListField(StringField(),default=list)
    message_id = StringField(max_length=200, required=True)
    parent_id = StringField(max_length=200, required=True)
    is_root = BooleanField(required=True)
    date = DateTimeField(default=datetime.datetime.now)
    body = StringField()
    subject = StringField()


    @classmethod
    def clean_body(self,body_text):
        lines = re.compile("[\n]").split(body_text)
        sentences_in_body = filter(lambda sentence: not self.is_part_of_trimmed_content(sentence),lines)
        body_content = reduce(lambda line1,line2: line1+ "\n" + line2,sentences_in_body)
        return body_content

    @classmethod
    def is_part_of_trimmed_content(self,line):
        trim_content_regex = re.compile("^>")
        mail_id_regex = re.compile("[_A-Za-z0-9-\\+]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})")
        if trim_content_regex.findall(line):
            return True

        if mail_id_regex.findall(line):
            return True

        return False


