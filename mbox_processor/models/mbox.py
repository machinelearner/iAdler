from mbox_processor.models import Mail,MailThread
from collections import defaultdict
import mailbox
from email.utils import parseaddr,parsedate,getaddresses
from datetime import datetime
from time import mktime
import re
from mail_insights.models import JaccardCoefficient

class Mbox:
    file_name = ""

    class Meta:
        app_label = 'mbox_processor'

    def __init__(self,file_name):
        self.file_name = file_name

    def parse_and_save(self):
        mbox = mailbox.mbox(self.file_name)
        mail_thread_hash = self.threadify(mbox)
        for thread_id,thread_hash in mail_thread_hash.iteritems():
            subject = thread_hash['subject']
            created_by = thread_hash['created_by']
            date_created = thread_hash['created_date']
            date_last_updated = thread_hash['updated_date']
            mails = thread_hash['mails']
            mails_in_thread = self.parse_list_of_mails(mails)
            MailThread.create_or_update(thread_id,subject,mails_in_thread,created_by,date_created,date_last_updated)

    def threadify(self,mbox):
        """Threadify only looking at thread_id"""
        mail_thread_hash = defaultdict(lambda : defaultdict(list))
        reply_regex= re.compile("^((R|r)(e|E):)")
        for mail in mbox:
            if ('In-Reply-To' in mail.keys() or 'References' in mail.keys()) and reply_regex.match(mail.get('Subject')):
                list_of_link_ids = []
                list_of_link_ids += self.get_in_reply_to(mail)
                list_of_link_ids += self.get_references_list(mail)
                matching_msg_id = list(set(list_of_link_ids) & set(mail_thread_hash.keys()))
                if len(matching_msg_id) == 0:
                    thread_id = self.get_thread_id_from_existing_threads(mail)
                    if not thread_id:
                        thread_id = self.get_thread_id_from_hash(mail_thread_hash,mail)
                    if thread_id == mail.get('Message-Id'):
                        self.add_new_thread_to_hash(mail_thread_hash,mail)
                else:
                    thread_list = filter(lambda x: x[0] in matching_msg_id,mail_thread_hash.iteritems())
                    thread_id = self.get_thread_id_from_thread_hash_by_subject(thread_list,mail)
                    if thread_id == mail.get('Message-Id'):
                        self.add_new_thread_to_hash(mail_thread_hash,mail)
            else:
                thread_id = mail.get('Message-Id')
                self.add_new_thread_to_hash(mail_thread_hash,mail)
            mail_thread_hash[thread_id]['updated_date'] = datetime.fromtimestamp(mktime(parsedate(mail.get('Date'))))
            mail_thread_hash[thread_id]['mails'].append(mail)

        return mail_thread_hash

    def add_new_thread_to_hash(self,thread_hash,mail):
        thread_id = mail.get('Message-Id')

        subject = mail.get('Subject')
        thread_hash[thread_id]['created_by'] = parseaddr(mail.get('From'))[-1]
        thread_hash[thread_id]['subject'] = subject
        thread_hash[thread_id]['created_date'] = datetime.fromtimestamp(mktime(parsedate(mail.get('Date'))))

    def get_thread_id_from_hash(self,mail_thread_hash,mail):
        reply_regex= re.compile("^((R|r)(e|E):)")
        subject = mail.get('Subject')
        if not subject:
            subject = "No Subject"

        subject = reply_regex.sub("",subject).strip()
        for thread_id, t_hash in mail_thread_hash.iteritems():
            if JaccardCoefficient.calculate(t_hash['subject'],subject)>0.66:
                return thread_id

        return mail.get('Message-Id')


    def get_thread_id_from_existing_threads(self,mail):
        list_of_link_ids = []
        not_reply_regex= re.compile("^(?!((R|r)(e|E):))")
        list_of_link_ids += self.get_references_list(mail)
        list_of_link_ids += self.get_in_reply_to(mail)
        list_of_mail_threads = MailThread.objects(thread_id__in=list_of_link_ids)
        if len(list_of_mail_threads) == 0:
            sub = not_reply_regex.sub("",mail.get('Subject')).strip()
            list_of_mts = MailThread.objects(subject=sub)
            if len(list_of_mts) == 0:
                return
            for mail_thread in list_of_mts:
                if(not_reply_regex.match(mail_thread.subject) or JaccardCoefficient.calculate(mail.get('Subject'),mail_thread.subject)>0.66):
                    return mail_thread.thread_id

        for mail_thread in list_of_mail_threads:
            if(not_reply_regex.match(mail_thread.subject) or JaccardCoefficient.calculate(mail.get('Subject'),mail_thread.subject)>0.66):
                return mail_thread.thread_id

        return list_of_mail_threads[0].thread_id

    def get_thread_id_from_thread_hash_by_subject(self,thread_list,mail):
        subject = mail.get('Subject')
        not_reply_regex = re.compile("^(?!((R|r)(e|E):))")
        thread_id = mail.get('Message-Id')
        if(not_reply_regex.match(subject)):
            return
        else:
            stripped_subject = not_reply_regex.sub("",subject).strip()
            if len(thread_list) == 0:
                return
            else:
                for mail_thread in thread_list:
                    if(JaccardCoefficient.calculate(stripped_subject,mail_thread[1]['subject'])>0.66):
                        thread_id = mail_thread[0]
                        break
        return thread_id

    def get_references_list(self,mail):
        references_list = mail.get('References')
        if not references_list:
            return []
        references_list = filter(lambda x: x not in ['\n','\t','\s',' '],references_list.split())
        return references_list

    def get_in_reply_to(self,mail):
        in_reply_to = mail.get('In-Reply-To')
        if not in_reply_to:
            return []
        in_reply_to = filter(lambda x: x not in ['\n','\t','\s',' '],in_reply_to.split())
        return in_reply_to

    def parse_list_of_mails(self,mails):
        body = ""
        mails_in_thread = []
        for mail in mails:
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

