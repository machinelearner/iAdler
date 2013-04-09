from mail_insights.models import TextProcessor
from collections import defaultdict

class MailDomainStatsGenerator():
    class Meta():
        app_label = "mail_insights"
    
    @classmethod
    def generate_number_of_questions_from_different_domains(self,mail_threads):
        number_of_questions_per_domain = defaultdict(int)
        creator_ids = map(lambda x: x.created_by, mail_threads)
        domain_list = map(lambda x: TextProcessor().extract_mail_domain(x), creator_ids)
        map(lambda name: number_of_questions_per_domain.update({name : number_of_questions_per_domain[name] + 1}),domain_list)
        return number_of_questions_per_domain
    
    @classmethod
    def generate_number_of_responses_from_different_domains(self,mail_threads):
        number_of_questions_per_domain = defaultdict(int)

        all_mails = reduce(lambda x,y: x+y,map(lambda x: x.mails,mail_threads))
        all_responder_mail_ids = map(lambda x: x.from_email,all_mails)
        domain_list = map(lambda x:TextProcessor().extract_mail_domain(x),all_responder_mail_ids)
        map(lambda name: number_of_questions_per_domain.update({name : number_of_questions_per_domain[name] + 1}),domain_list)
        return number_of_questions_per_domain

