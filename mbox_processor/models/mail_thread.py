from mongoengine import *
from mbox_processor.models import Mail
import datetime

class MailThread(DynamicDocument):
    class Meta:
        app_label = 'mbox_processor'

    subject = StringField(max_length=200, required=True,default="No Subject Found")
    date_created = DateTimeField(default=datetime.datetime.now)
    created_by = StringField()
    mails = ListField(EmbeddedDocumentField(Mail))
    thread_id = StringField()
    """thread-id is the message-id of the first message which started the thread"""

    @classmethod
    def create_or_update(self,thread_id,subject,mails,created_by,date_created):
        mail_thread = self.objects.filter(thread_id=thread_id).first()
        print(mail_thread)
        if not mail_thread:
            mail_thread = MailThread(thread_id=thread_id,mails=mails,subject=subject,created_by=created_by,date_created=date_created)
            mail_thread.save()
        else:
            for mail in mails:
                mail_thread.update(add_to_set__mails=mail)
                mail_thread.save()
