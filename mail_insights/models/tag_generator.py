from mail_insights.models import Annotation,TextProcessor,UnigramDistribution
from collections import defaultdict
import math

class TagGenerator:
    class Meta:
        app_label = 'mail_insights'

    @classmethod
    def generate_using_tfidf(self,document,number_of_documents,TagClass=Annotation):
        text_processor = TextProcessor()
        tokens = text_processor.tokenize(document)
        annotations = TagClass.objects(word__in=tokens)
        tfidf_hash = defaultdict(float)
        map(lambda annotation: tfidf_hash.update({annotation.word:annotation.tfidf(number_of_documents)}),annotations)
        sorted_tag_tuples = map(lambda key: (key,tfidf_hash[key]), sorted(tfidf_hash,key=tfidf_hash.get,reverse=True))
        return sorted_tag_tuples[:5]

    @classmethod
    def generate_using_ICA(self,document_to_tag,documents_in_corpus,TagClass=Annotation):
        text_processor = TextProcessor()
        tokens = text_processor.tokenize(document_to_tag)
        tf_for_given_document = UnigramDistribution.generate_tf_for_document(document_to_tag)
        tf_across_documents = map(lambda document: UnigramDistribution.generate_tf_for_document(document),documents_in_corpus)
        token_weight = defaultdict(float)
        annotations = TagClass.objects(word__in=tokens)
        for annotation in annotations:
            median_weight = annotation.term_frequency/float(annotation.document_frequency)
            list_of_deviation_square = map(lambda tf_hash: math.pow((tf_hash[annotation.word] - median_weight),2),tf_across_documents)
            token_weight[annotation.word] = tf_for_given_document[annotation.word] * math.sqrt(reduce(lambda x,y:x+y,list_of_deviation_square))
        sorted_tag_tuples = map(lambda key: (key,token_weight[key]), sorted(token_weight,key=token_weight.get,reverse=True))
        return sorted_tag_tuples[:10]


