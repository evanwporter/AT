import spacy
import en_core_web_sm

from util.search_tweets import TweetSearcher

class SentimentAnalyzer:
    nlp = en_core_web_sm.load()

    def __init__(self, source):
        self.source = source

    def get_data(self, source):
        if source == 'twitter':
            pass
    def clean(self, article):
        for paragraph in article:
            paragraph = self.nlp(unparsed_article[paragraph]).sents
            for sentence in paragraph:
                # Makes sure sentence isn't empty
                if sentence:
                    yield sentence.replace("  ", " ")