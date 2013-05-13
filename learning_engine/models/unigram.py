from mongoengine import *
from learning_engine.models import ClassScore

class Unigram(DynamicDocument):
    word = StringField()
    class_scores = ListField(EmbeddedDocumentField(ClassScore))

    class Meta:
        app_label = 'learning_engine'
    
    def get_probability_for_label(self,label):
        for class_score in self.class_scores:
            if class_score.label == label:
                return class_score.probability
