from mongoengine import *
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
        app_label = 'mail_insights'

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
