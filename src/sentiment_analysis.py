from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

def sentiment_analysis(articles, symbols, method='VADER'):
    if method.lower() == 'VADER':
        filtered_list = {
            symbol: [
                sentence 
                for article in articles 
                for paragraph in article
                for sentence in paragraph
                if symbol in sentence.lower()
            ] for symbol in symbols
        }

        scores = {symbol: analyser.polarity_scores(' '.join(filtered_list[symbol])) for symbol in symbols}
        return scores