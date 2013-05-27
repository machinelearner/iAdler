from learning_engine.models import Annotation
from utils import TextProcessor,UnigramDistribution
from collections import defaultdict
import math

class TagGenerator:
    class Meta:
        app_label = 'learning_engine'

    @classmethod
    def generate_using_TFIDF(self,document,number_of_documents,TagClass=Annotation):
        text_processor = TextProcessor()
        tokens = text_processor.tokenize(document)
        annotations = TagClass.objects(word__in=tokens)
        return self.get_top_10_TFIDF_based_tags(annotations,number_of_documents)

    @classmethod
    def get_top_10_TFIDF_based_tags(self,annotations,number_of_documents):
        tfidf_hash = defaultdict(float)
        map(lambda annotation: tfidf_hash.update({annotation.word:annotation.tfidf(number_of_documents)}),annotations)
        sorted_tag_tuples = map(lambda key: (key,tfidf_hash[key]), sorted(tfidf_hash,key=tfidf_hash.get,reverse=True))
        return sorted_tag_tuples[:10]


    @classmethod
    def generate_using_ICA(self,document_to_tag,documents_in_corpus,TagClass=Annotation):
        text_processor = TextProcessor()
        tokens = text_processor.extract_nouns(document_to_tag)
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

    @classmethod
    def generate_all_using_ICA(self,documents_in_corpus,tf_across_documents,TagClass=Annotation):
        tags_for_documents = defaultdict(list)
        for subject,document in documents_in_corpus.iteritems():
            tokens = tf_across_documents[subject].keys()
            tf_for_given_document = tf_across_documents[subject]
            token_weight = defaultdict(float)
            annotations = TagClass.objects(word__in=tokens)
            for annotation in annotations:
                median_weight = annotation.term_frequency/float(annotation.document_frequency)
                list_of_deviation_square = map(lambda tf_hash: math.pow((self.get_dict_val(tf_hash,annotation.word) - median_weight),2),tf_across_documents.values())
                token_weight[annotation.word] = tf_for_given_document[annotation.word] * math.sqrt(reduce(lambda x,y:x+y,list_of_deviation_square))
            sorted_tag_tuples = map(lambda key: (key,token_weight[key]), sorted(token_weight,key=token_weight.get,reverse=True))
            tags_for_documents[subject] = sorted_tag_tuples[:10]
            print "." * len(annotations)
        return tags_for_documents

    @classmethod
    def generate_all_using_TFIDF(self,documents_in_corpus,tf_across_documents,TagClass=Annotation):
        tags_for_documents = defaultdict(list)
        for subject,document in documents_in_corpus.iteritems():
            tokens = tf_across_documents[subject].keys()
            annotations = TagClass.objects(word__in=tokens)
            tags_for_documents[subject] = self.get_top_10_TFIDF_based_tags(annotations,len(documents_in_corpus))
            print "." * len(annotations)
        return tags_for_documents


    @classmethod
    def get_dict_val(self,dictionary,key):
        if key in dictionary.keys():
            return dictionary[key]
        return 0
