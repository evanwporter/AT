import re

import tweepy
from twitter_scraper import get_tweets

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dataclasses import dataclass

class TweetSearcher(object):
    """ 
    Generic Twitter Class for sentiment analysis. 
    """

    def __init__(self):
        """ 
        Class constructor or initialization method. 
        """
        self.analyzer = SentimentIntensityAnalyzer()

    @staticmethod
    def _clean_tweet(tweet: str):
        """ 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        """
        return re.sub(
            r"(@[A-Za-z0-9]+)|(\w+://\S+)|(\n)", " ", tweet
        )

    def scrape_tweets(self, query):
        tweets = []
        # call twitter api to fetch tweets
        fetched_tweets = get_tweets(query=query)

        # parsing tweets one by one
        for tweet in fetched_tweets:
            tweet['text'] = self._clean_tweet(tweet['text'])

            tweet['sentiment'] = self.analyzer.polarity_scores(tweet['text'])

            # appending parsed tweet to tweets list
            if tweet['retweets'] > 0:
                # if tweet has retweets, ensure that it is appended only once
                if tweet not in tweets:
                    tweets.append( 
                        tweet
                    )
            else:
                tweets.append(tweet)
        return tweets

# @dataclass
# class Tweet:
#     date: str
#     text: str
#     # times_quoted: int
#     # number_replies: int
#     times_retweeted: int
#     number_likes: int
#     sentiment = analyser.polarity_scores(text)
