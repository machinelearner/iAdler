from mail_insights.models import TextProcessor

class JaccardCoefficient():

    class Meta:
        app_label = 'mail_insights'

    @staticmethod
    def calculate(sentence1,sentence2):
        if not(sentence1 and sentence2):
            return 0
        tokens1 = TextProcessor().no_stop_tokens(sentence1)
        tokens2 = TextProcessor().no_stop_tokens(sentence2)
        cardinality_of_intersection = len(set(tokens1) & set(tokens2))
        cardinality_of_union = len(set(tokens1) | set(tokens2))
        jIndex = round(cardinality_of_intersection/float(cardinality_of_union),4)
        return jIndex


