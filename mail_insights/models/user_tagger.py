from mbox_processor.models import MailThread
from learning_engine.models import ClassLabel
from collections import defaultdict

class UserTopicsTagger():

    @classmethod
    def tag_for_associated_topics_ICA(self,user):
        mail_threads = MailThread.objects
        associated_ICA_tags = []
        for thread in mail_threads:
            if thread.is_associated_user(user):
                associated_ICA_tags += thread.tags_ICA
        associated_ICA_tags = list(set(associated_ICA_tags))
        user.associated_ICA_tags = associated_ICA_tags
        user.save()

    @classmethod
    def tag_all_for_associated_topics_ICA(self):
        mail_threads = MailThread.objects
        print "threads loaded"
        user_topic_hash = defaultdict(lambda: [None,[]])
        for a_thread in mail_threads:
            users_in_thread = a_thread.users_in_thread()
            for a_user in users_in_thread:
                user_topic_hash[a_user.email][0] = a_user
                user_topic_hash[a_user.email][1] += a_thread.tags_ICA
            print a_thread.subject
        for user_topic_association in user_topic_hash.values():
            associated_ICA_tags = list(set(user_topic_association[1]))
            user = user_topic_association[0]
            user.associated_ICA_tags = associated_ICA_tags
            user.save()
            print user.name, "         ", user.associated_ICA_tags

    @classmethod
    def tag_bounty_levels_ICA(self,user,bounty_levels=ClassLabel.objects.distinct("name")):
        threads_per_bounty_level = dict((a_level,0) for a_level in bounty_levels)
        mail_threads = MailThread.objects
        for a_thread in mail_threads:
            if a_thread.is_associated_user(user):
                threads_per_bounty_level[a_thread.difficulty_level_ICA] += 1
        user.threads_per_bounty_level_ICA = threads_per_bounty_level
        user.save()

    @classmethod
    def tag_bounty_levels_TFIDF(self,user,bounty_levels=ClassLabel.objects.distinct("name")):
        threads_per_bounty_level = dict((a_level,0) for a_level in bounty_levels)
        mail_threads = MailThread.objects
        for a_thread in mail_threads:
            if a_thread.is_associated_user(user):
                threads_per_bounty_level[a_thread.difficulty_level_TFIDF] += 1
        user.threads_per_bounty_level_TFIDF = threads_per_bounty_level
        user.save()

    @classmethod
    def tag_all_for_bounty_levels_ICA(self,bounty_levels=ClassLabel.objects.distinct("name")):
        mail_threads = MailThread.objects
        print "threads loaded"
        user_bounty_hash = defaultdict(lambda: [None,dict((a_level,0) for a_level in bounty_levels)])
        for a_thread in mail_threads:
            users_in_thread = a_thread.users_in_thread()
            for a_user in users_in_thread:
                user_bounty_hash[a_user.email][0] = a_user
                user_bounty_hash[a_user.email][1][a_thread.difficulty_level_ICA] += 1
            print a_thread.subject
        for user_bounty_association in user_bounty_hash.values():
            threads_per_bounty_level= user_bounty_association[1]
            user = user_bounty_association[0]
            user.threads_per_bounty_level_ICA = threads_per_bounty_level
            user.save()
            print user.name, "         ", user.threads_per_bounty_level_ICA

    @classmethod
    def tag_all_for_bounty_levels_TFIDF(self,bounty_levels=ClassLabel.objects.distinct("name")):
        mail_threads = MailThread.objects
        print "threads loaded"
        user_bounty_hash = defaultdict(lambda: [None,dict((a_level,0) for a_level in bounty_levels)])
        for a_thread in mail_threads:
            users_in_thread = a_thread.users_in_thread()
            for a_user in users_in_thread:
                user_bounty_hash[a_user.email][0] = a_user
                user_bounty_hash[a_user.email][1][a_thread.difficulty_level_TFIDF] += 1
            print a_thread.subject
        for user_bounty_association in user_bounty_hash.values():
            threads_per_bounty_level= user_bounty_association[1]
            user = user_bounty_association[0]
            user.threads_per_bounty_level_TFIDF = threads_per_bounty_level
            user.save()
            print user.name, "         ", user.threads_per_bounty_level_TFIDF


