import math
from utils import TextProcessor,UnigramDistribution
from learning_engine.models import Unigram,ClassScore,ClassLabel
import operator
from collections import defaultdict

class NBClassifier():
    labelled_training_set = defaultdict(list) 
   
    def __init__(self,labelled_training_set):
       self.labelled_training_set = labelled_training_set
       self.classes = self.labelled_training_set.keys()

    def train(self):
        term_frequency_per_class = defaultdict(list)
        for label in self.classes:
            term_frequency_per_class[label] = UnigramDistribution.generate_tf_of_nouns(self.labelled_training_set[label])
        self.create_class_labels(self.classes)
        self.create_classwise_unigram_probabilities(term_frequency_per_class)
            
    @classmethod
    def classify(self,text):
        tokens = map(lambda x: TextProcessor().removeNonAscii(x).lower(),TextProcessor().tokenize(text))
        unigrams = Unigram.objects(word__in=tokens)
        all_classes =  ClassLabel.objects.distinct("name")
        #belongingness_probability = dict((label,0) for label in Unigram.objects.distinct('label'))
        #for label in unigrams:
            #belongingness_probability[label] = self.probability_union(map(lambda x: x.probability,unigrams))
        #classified_label = max(belongingness_probability,key=belongingness_probability.get)
        #return classified_label
        belongingness_probability = dict((a_class,0) for a_class in all_classes)
        for a_class in all_classes:
            list_of_probabilities = []
            for unigram in unigrams:
                list_of_probabilities.append(unigram.get_probability_for_label(a_class))
#            belongingness_probability[a_class] = self.probability_union(list_of_probabilities)
            belongingness_probability[a_class] = self.log_values(list_of_probabilities)
        classified_label = max(belongingness_probability,key=belongingness_probability.get)
        return classified_label, belongingness_probability[classified_label]

    @staticmethod
    def probability_union(list_of_probabilities):
        union = reduce(operator.mul,list_of_probabilities,1)
        return union

    @staticmethod
    def log_values(list_of_probabilities):
        union = reduce(lambda x,y:x+y,map(lambda x: math.log10(x),list_of_probabilities))
        return union


    def create_classwise_unigram_probabilities(self,term_frequency_per_class):
        all_tokens = reduce(lambda x,y: x+y, map(lambda tf_hash: tf_hash.keys(),term_frequency_per_class.values()))
        denominator_per_class_with_smoothing = self.extract_denominator_from_term_freq_hash(term_frequency_per_class)
        all_classes = term_frequency_per_class.keys()
        for token in all_tokens:
            class_scores = []
            for a_class in all_classes:
                frequency = term_frequency_per_class[a_class][token] 
                probability = (frequency + 1)/(denominator_per_class_with_smoothing[a_class] * 1.0)
                class_scores.append(ClassScore(label=a_class,frequency=frequency,probability=probability))
            Unigram(word=TextProcessor().removeNonAscii(token),class_scores=class_scores).save()

    def extract_denominator_from_term_freq_hash(self,term_frequency_per_class):
        smoothed_denominator_per_class = defaultdict(lambda: 1)
        for a_class, tf_hash in term_frequency_per_class.iteritems():
            #smoothed_denominator_per_class[a_class] = reduce(lambda x,y: x+y,map(lambda tf: tf + 1,tf_hash.values()))
            smoothed_denominator_per_class[a_class] = reduce(lambda x,y: x+y,map(lambda tf: tf,tf_hash.values()))
        return smoothed_denominator_per_class

    def create_class_labels(self,classes):
        for a_class in classes:
            ClassLabel(name=a_class).save()

from mongoengine import register_connection,connect
connect("iAdler_development")
register_connection(alias="iAdler_development",name="iAdler_development")

begin = open("/Users/Admin/TW/iAdler/data/domain_difficulty/advanced.txt")
NBClassifier.classify(begin.read())