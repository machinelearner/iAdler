from mbox_processor.models import Mail,MailThread
from collections import defaultdict
import mailbox
from email.utils import parseaddr,parsedate,getaddresses
from datetime import datetime
from time import mktime
from jwzthreading import *

class Mbox:
    file_name = ""

    class Meta:
        app_label = 'mbox_processor'

    def __init__(self,file_name):
        self.file_name = file_name

    def threadify_using_jwz_and_save(self):
        mbox = mailbox.mbox(self.file_name)
        messages = []
        for mail in mbox:
            messages.append(make_message(mail))
        jwz_table = thread(messages)
        for thread_id,thread_container in jwz_table.iteritems():
            self.create_thread(thread_id,thread_container)

    def create_thread(self,thread_id,thread_container):
        subject = thread_id
        thread_info = self.get_thread_info(thread_container)
        created_by = thread_info['created_by']
        date_created = thread_info['created_date']
        mails_in_thread = self.mails_from_container(thread_container,is_root=True)
        MailThread.create_or_update(thread_id,subject,mails_in_thread,created_by,date_created)

    def mails_from_container(self,container,is_root=False):
        mails = []
        if container.message:
            mail = self.create_mail_document(container.message.message)
            mail.parent_id = self.get_parent_mail_id(container,is_root)
            mail.is_root = is_root
            mails += [mail]
        for child in container.children:
            mails += self.mails_from_container(child)
        return mails


    def get_charset(self,message, default="ascii"):
        """'Get the message charset'"""

        if message.get_content_charset():
            return message.get_content_charset()

        if message.get_charset():
            return message.get_charset()

        return default

    def get_body_from_multipart_mail(self,mail):
        body = ""
        for part in mail.get_payload():
            if(part.get_content_type() == "text/plain"):
                body += unicode(part.get_payload(decode=True),self.get_charset(mail),"replace")
                body += "\n"
        return body


    def create_mail_document(self,mail):
        body = ""
        if(mail.is_multipart()):
            body = self.get_body_from_multipart_mail(mail)
        else:
            body = unicode(mail.get_payload(decode=True),self.get_charset(mail),"replace")
        from_email = parseaddr(mail.get('From'))[1]
        if(mail.get_all('Cc')):
            ccs_string = mail.get_all('Cc')
        else:
            ccs_string = ''
        if(mail.get_all('To')):
            tos_string = mail.get_all('To')
        else:
            tos_string = ''
        cc_emails = map(lambda addr:addr[1],getaddresses(ccs_string))
        to_emails = map(lambda addr:addr[1],getaddresses(tos_string))
        from_user = parseaddr(mail.get('From'))[0]
        subject = mail.get('Subject')
        message_id = mail.get('Message-Id')
        date = datetime.fromtimestamp(mktime(parsedate(mail.get('Date'))))
        body = Mail.clean_body(body)
        mail_document = Mail(message_id=message_id,body=body,to=to_emails,from_user=from_user,from_email=from_email,cc=cc_emails,subject=subject,date=date)
        return mail_document


    def get_thread_info(self,thread_container):
        thread_info = defaultdict(str)
        if thread_container.message:
            thread_start = thread_container.message.message
        else:
            thread_start = thread_container.children[0].message.message

        thread_info['created_by'] = parseaddr(thread_start.get('From'))[-1]
        thread_info['created_date'] = datetime.fromtimestamp(mktime(parsedate(thread_start.get('Date'))))
        return thread_info

    def get_parent_mail_id(self,container,is_root):
        if is_root:
            return container.message.message_id
        else:
            if container.parent.message:
                return container.parent.message.message_id
        return container.message.message_id


#Mbox("./data/201304.mbox").threadify_using_jwz()
