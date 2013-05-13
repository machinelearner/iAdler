from svm import *
from svmutil import *
import os
import learning_engine
from utils import TextProcessor
import sys

class QuestionIdentifier():
    training_file_name = ""
    model_file_name = ""
    trained = False
    DATA_DIR = os.path.abspath(learning_engine.__path__[0])
    model = None

    class Meta:
        app_label = "learning_engine"

    def __init__(self,training_file,model_file=DATA_DIR+"/data/questionIDModel.model"):
        self.training_file_name = training_file
        self.model_file_name = model_file

    def train(self):
        try:
            training_file = open(self.training_file_name,"r")
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return
        feature_vectors = []
        for line in training_file.readlines():
            feature_vector = self.extract_question_features(line)
            feature_vectors.append(feature_vector)
        labels = [0] * len(feature_vectors)
        problem = svm_problem(labels,feature_vectors)
        one_class_svm_model_parameters = svm_parameter('-s 2 -t 2')
        self.model = svm_train(problem,one_class_svm_model_parameters)
        svm_save_model(self.model_file_name,self.model)
        self.trained = True
        print "Training Complete"

    def is_question(self,sentence):
        if not self.trained or not self.model:
            print "Question Identifier is not trained to identify question. Use the train method to train agains a set of sample questions"
            return
        feature_vector = self.extract_question_features(sentence)
        prediction_labels,prediction_accuracy,prediction_values = svm_predict([1],[feature_vector],self.model)
        return prediction_labels

    def extract_question_features(self,line):
        line = line.strip()
        text_processor = TextProcessor()
        #if text_processor.is_compound(line):
        #    line = text_processor.extract_simple_question_phrase(line)
        contains_5wh1 = text_processor.contains_5wh1(line)
        starts_with_5wh1 = text_processor.starts_with_5wh1(line)
        starts_with_modal = text_processor.starts_with_modal(line)
        #verb_exists_after_5wh1 = text_processor.verb_exists_after_5wh1(line)
        #noun_or_pronoun_exists_after_5wh1 = text_processor.noun_or_pronoun_exists_after_5wh1(line)
        #start_5wh1_weight = text_processor.distance_from_beginning_5wh1(line)
        #end_5wh1_weight = text_processor.distance_from_end_5wh1(line)
        ends_with_5wh1 = text_processor.ends_with_5wh1(line)
        if line[-1] == '?':
            has_question_mark = 1
        else:
            has_question_mark = 0
        return [contains_5wh1,starts_with_5wh1,starts_with_modal,ends_with_5wh1,has_question_mark]
        #return [contains_5wh1,start_5wh1_weight,starts_with_modal,end_5wh1_weight,has_question_mark]

