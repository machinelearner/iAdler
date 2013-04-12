from collections import defaultdict

class UserStatsGenerator:
    class Meta:
        app_label = "mail_insights"
    @classmethod
    def generate_number_of_responses_from_different_users(self,mail_threads):
        questions_per_user_hash = defaultdict(int)
        all_mails = reduce(lambda x,y: x+y,map(lambda x: x.mails,mail_threads))
        user_list = map(lambda mail: mail.extract_user_name(),all_mails)
        map(lambda name: questions_per_user_hash.update({name : questions_per_user_hash[name] + 1}),user_list)
        users_in_decending_order = sorted(questions_per_user_hash,key=questions_per_user_hash.get,reverse=True)
        number_of_questions_per_user = map(lambda user: (user,questions_per_user_hash[user]),users_in_decending_order)
        return number_of_questions_per_user

