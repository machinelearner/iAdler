from mbox_processor.models import *
from collections import defaultdict
import mailbox
from email.utils import parseaddr,parsedate,getaddresses
from datetime import datetime
from time import mktime

class Mbox:
    file_name = ""

    def __init__(self,file_name):
        self.file_name = file_name

    def parse_and_save(self):
        mbox = mailbox.mbox(self.file_name)
        mail_thread_hash = self.threadify(mbox)
        for thread_id,mails in mail_thread_hash.iteritems():
            subject = mails[0]['Subject']
            created_by = parseaddr(mails[0]['From'])[1]
            date_created = datetime.fromtimestamp(mktime(parsedate(mails[0].get('Date'))))
            date_last_updated = datetime.fromtimestamp(mktime(parsedate(mails[-1].get('Date'))))
            mails_in_thread = self.parse_list_of_mails(mails)
            MailThread.create_or_update(thread_id,subject,mails_in_thread,created_by,date_created,date_last_updated)

    def threadify(self,mbox):
        mail_thread_hash = defaultdict(list)
        for mail in mbox:
            if('In-Reply-To' in mail.keys()):
                thread_id = mail['In-Reply-To']
                mail_thread_hash[thread_id].append(mail)
            else:
                message_id = mail['Message-Id']
                mail_thread_hash[message_id].append(mail)
        return mail_thread_hash

    def parse_list_of_mails(self,mails):
        body = ""
        mails_in_thread = []
        for mail in mails:
            if(mail.is_multipart()):
                body = self.get_body_from_multipart_mail(mail)
            else:
                body = unicode(mail.get_payload(decode=True),self.get_charset(mail),"replace")
            from_email = parseaddr(mail['From'])[1]
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
            from_user = parseaddr(mail['From'])[0]
            subject = mail['Subject']
            message_id = mail['Message-Id']
            date = datetime.fromtimestamp(mktime(parsedate(mail.get('Date'))))
            mail_document = Mail(message_id=message_id,body=body,to=to_emails,from_user=from_user,from_email=from_email,cc=cc_emails,subject=subject,date=date)
            mails_in_thread.append(mail_document)
        return mails_in_thread

    def get_body_from_multipart_mail(self,mail):
        body = ""
        for part in mail.get_payload():
            if(part.get_content_type() == "text/plain"):
                body += unicode(part.get_payload(decode=True),self.get_charset(mail),"replace")
                body += "\n"
        return body

    def get_charset(self,message, default="ascii"):
        """Get the message charset"""

        if message.get_content_charset():
            return message.get_content_charset()

        if message.get_charset():
            return message.get_charset()

        return default
