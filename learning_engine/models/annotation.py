from mongoengine import *
from utils import UnigramDistribution
import math
#from collections import defaultdict

class Annotation(DynamicDocument):
    WORD_TYPE = (
            ('cue','cue-word'),
            ('ne','noun'),
            )
    word = StringField()
    term_frequency = FloatField()
    document_frequency = FloatField()
    word_type = StringField()

    class Meta:
        app_label = 'learning_engine'

    def tfidf(self,number_of_documents):
        tfidf = (self.term_frequency/self.max_tf()) * math.log(((number_of_documents + 1)/self.document_frequency),2)
        return round(tfidf,4)

    @classmethod
    def max_tf(self):
        return self.objects().order_by('-term_frequency')[0].term_frequency

    #@classmethod
    #def get_top_10_tfidf_tokens_from_list(self,word_list):
        #annotations = self.objects.filter(word__in=word_list)
        #annotation_tfidf_map = defaultdict(float)
        #map(lambda annot: annotation_tfidf_map.update({annot.word:annot.tfidf}),annotations)
        #return sorted(annotation_tfidf_map.keys(), key=annotation_tfidf_map.get)[:10]

    @staticmethod
    def generate_tf_df_for_mail_threads(mailThread_objects):
        Annotation.objects.delete()
        all_mails = reduce(lambda x,y: x+y,map(lambda x:
            x.mails,mailThread_objects))
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
