from mail_insights.models import Annotation,TextProcessor
from mbox_processor.models import MailThread
from collections import defaultdict,OrderedDict

class UnigramDistribution():

    class Meta:
        app_label = 'mail_insights'

    @staticmethod
    def increment_distribution(distribution,key):
        distribution[key] += 1

    @staticmethod
    def generate_tf_of_nouns(documents):
        tf = defaultdict(int)
        for document in documents:
            tokens = TextProcessor().extract_nouns(document)
            [UnigramDistribution.increment_distribution(tf,token.lower()) for token in tokens]
        return tf

    @staticmethod
    def generate_tf_for_document(document):
        tf = defaultdict(int)
        tokens = TextProcessor().tokenize(document)
        [UnigramDistribution.increment_distribution(tf,token.lower()) for token in tokens]
        return tf

    @staticmethod
    def generate_df_of_nouns(documents):
        df = defaultdict(int)
        for document in documents:
            tokens =  TextProcessor().extract_nouns(document)
            [UnigramDistribution.increment_distribution(df,token.lower()) for token in OrderedDict.fromkeys(tokens).keys()]
        return df

    @staticmethod
    def generate_tf_df_for_mail_threads():
        Annotation.objects.delete()
        all_mails = reduce(lambda x,y: x+y,map(lambda x: x.mails,MailThread.objects()))
        documents = map(lambda x: x.body,all_mails)
        tf = UnigramDistribution.generate_tf_of_nouns(documents)
        df = UnigramDistribution.generate_df_of_nouns(documents)
        for token in tf.keys():
            annotation = Annotation(word=token,term_frequency=tf[token],document_frequency=df[token],word_type=Annotation.WORD_TYPE[1][1])
            annotation.save()

    @staticmethod
    def max_tfidf():
        max_tfidf = -1
        annotations = Annotation.objects()
        for annotation in annotations:
            tfidf = annotation.tfidf()
            max_tfidf = tfidf if max_tfidf < tfidf else max_tfidf
        return max_tfidf
