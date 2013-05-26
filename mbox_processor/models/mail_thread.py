from mongoengine import *
from mbox_processor.models import User,Mail
import datetime
from collections import defaultdict
from functools import partial
from utils import UnigramDistribution

class MailThread(DynamicDocument):
    class Meta:
        app_label = 'mbox_processor'

    subject = StringField(max_length=200, required=True,default="No Subject Found")
    date_created = DateTimeField(default=datetime.datetime.now)
    creator = ReferenceField(User,required=True)
    mails = ListField(EmbeddedDocumentField(Mail))
    thread_id = StringField()
    term_frequencies = DictField()
    tags_ICA_in_domain_difficulty = ListField(StringField(default=["Miscellaneous","Unrelated"]))
    """thread-id is the message-id of the first message which started the thread"""

    @classmethod
    def create_or_update(self,thread_id,subject,mails,creator_email,creator_name,date_created):
        mail_thread = self.objects.filter(thread_id=thread_id).first()
        print(mail_thread)
        if not mail_thread:
            thread_content = reduce(lambda mail1,mail2: mail1 + "\n" + mail2,map(lambda mail: mail.body,mails)) + "\n" + subject
            term_frequencies = UnigramDistribution.generate_tf_for_document(thread_content)
            creator,obj_created_status = User.objects.get_or_create(email=creator_email,auto_save=False)
            print "###############",creator,obj_created_status
            if obj_created_status:
                creator.name = creator_name
                creator.save()
            mail_thread = MailThread(thread_id=thread_id,mails=mails,subject=subject,creator=creator,date_created=date_created,term_frequencies=term_frequencies)
            mail_thread.save()
        else:
            old_term_frequencies = mail_thread.term_frequencies
            new_thread_content = reduce(lambda mail1,mail2: mail1 + "\n" + mail2,map(lambda mail: mail.body,mails))
            new_term_frequencies = UnigramDistribution.generate_tf_for_document(new_thread_content)
            term_frequencies = self.updated_term_frequencies(old_term_frequencies,new_term_frequencies)
            mail_thread.term_frequencies = term_frequencies
            for mail in mails:
                mail_thread.update(add_to_set__mails=mail)
                mail_thread.save()

    @classmethod
    def get_thread_content_for_all_mail_threads(self):
        mail_threads = self.objects
        thread_content = defaultdict(list)
        for a_thread in mail_threads:
            subject = a_thread.subject
            thread_content[subject] = reduce(lambda x,y: x + "\n" + y,map(lambda mail: mail.body,a_thread.mails)) + "\n" + subject
        return thread_content

    @classmethod
    def updated_term_frequencies(self,old_term_frequencies,new_term_frequencies):
        for key in new_term_frequencies.keys():
            old_term_frequencies[key] += new_term_frequencies[key]
        return old_term_frequencies

    @classmethod
    def get_tf_for_all_mail_threads(self):
        mail_threads = self.objects.only("term_frequencies","subject")
        all_term_frequencies = defaultdict(partial(defaultdict,int))
        map(lambda mt: self.update_freq(all_term_frequencies,mt),mail_threads)
        return all_term_frequencies

    @classmethod
    def update_freq(self, all_term_frequencies, thread):
        all_term_frequencies[thread.subject] = thread.term_frequencies

