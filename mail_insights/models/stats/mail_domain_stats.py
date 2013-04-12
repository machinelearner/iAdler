from mail_insights.models import TextProcessor
from collections import defaultdict
import re

class MailDomainStatsGenerator():
    class Meta():
        app_label = "mail_insights"

    @classmethod
    def generate_number_of_questions_from_different_domains(self,mail_threads):
        questions_per_domain_hash = defaultdict(int)
        reply_regex = re.compile("^(?!((R|r)(e|E):))")
        mail_threads = filter(lambda x: reply_regex.match(x.subject), mail_threads)
        creator_ids = map(lambda x: x.created_by, mail_threads)
        domain_list = map(lambda x: TextProcessor().extract_mail_domain(x), creator_ids)
        map(lambda name: questions_per_domain_hash.update({name : questions_per_domain_hash[name] + 1}),domain_list)
        domains_in_decending_order = sorted(questions_per_domain_hash,key=questions_per_domain_hash.get,reverse=True)
        number_of_questions_per_domain = map(lambda domain: (domain,questions_per_domain_hash[domain]),domains_in_decending_order)

        return number_of_questions_per_domain

    @classmethod
    def generate_number_of_responses_from_different_domains(self,mail_threads):
        questions_per_domain_hash = defaultdict(int)
        all_mails = reduce(lambda x,y: x+y,map(lambda x: x.mails,mail_threads))
        all_responder_mail_ids = map(lambda x: x.from_email,all_mails)
        domain_list = map(lambda x:TextProcessor().extract_mail_domain(x),all_responder_mail_ids)
        map(lambda name: questions_per_domain_hash.update({name : questions_per_domain_hash[name] + 1}),domain_list)
        domains_in_decending_order = sorted(questions_per_domain_hash,key=questions_per_domain_hash.get,reverse=True)
        number_of_questions_per_domain = map(lambda domain: (domain,questions_per_domain_hash[domain]),domains_in_decending_order)
        return number_of_questions_per_domain

