from utils import TextProcessor
from collections import defaultdict,OrderedDict

class UnigramDistribution():

    #class Meta:
        #app_label = 'mail_insights'

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

