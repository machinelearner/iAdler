from learning_engine.models import TagGenerator,Unigram,NBClassifier
from mbox_processor.models import MailThread

class MailTagger():

    class Meta:
        app_label = "mail_insights"

    @classmethod
    def tag_mail_thread_by_concepts(self):
        thread_content = MailThread.get_thread_content_for_all_mail_threads()
        tf_across_documents = MailThread.get_tf_for_all_mail_threads()
        print "loaded threads"
        thread_tags = TagGenerator.generate_all_using_ICA(thread_content,tf_across_documents)
        for subject,thread_body in thread_content.iteritems():
            tags_for_thread = map(lambda x: x[0],thread_tags[subject])
            difficulty_tags = Unigram.objects(word__in=tags_for_thread).distinct('word')
            thread = MailThread.objects.get(subject=subject)
            thread.tags_ICA = tags_for_thread
            thread.tags_ICA_in_domain_difficulty  = difficulty_tags
            thread.save()

    @classmethod
    def tag_mail_thread_for_difficulty_level_using_ICA_tags(self):
        mail_threads = MailThread.objects
        for thread in mail_threads:
            classified_label = NBClassifier.classify_tokens(thread.tags_ICA_in_domain_difficulty)
            thread.difficulty_level_ICA = classified_label[0]
            print "." * len(thread.tags_ICA_in_domain_difficulty)
            thread.save()

    @classmethod
    def tag_mail_thread_for_difficulty_level_using_TFIDF_tags(self):
        mail_threads = MailThread.objects
        for thread in mail_threads:
            classified_label = NBClassifier.classify_tokens(thread.tags_TFIDF_in_domain_difficulty)
            thread.difficulty_level_TFIDF = classified_label[0]
            print "." * len(thread.tags_TFIDF_in_domain_difficulty)
            thread.save()

    @classmethod
    def tag_mail_thread_by_term_occurrence(self):
        thread_contents = MailThread.get_thread_content_for_all_mail_threads()
        tf_across_documents = MailThread.get_tf_for_all_mail_threads()
        print "loaded threads"
        thread_tags = TagGenerator.generate_all_using_TFIDF(thread_contents,tf_across_documents)
        for subject,thread_body in thread_contents.iteritems():
            tags_for_thread = map(lambda x: x[0],thread_tags[subject])
            difficulty_tags = Unigram.objects(word__in=tags_for_thread).distinct('word')
            thread = MailThread.objects.get(subject=subject)
            thread.tags_TFIDF = tags_for_thread
            thread.tags_TFIDF_in_domain_difficulty  = difficulty_tags
            thread.save()

