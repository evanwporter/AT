import requests
import feedparser
import lxml.html

import re

import pandas as pd
import numpy as np

article_classes: {
    'forbes': 'article-body',
    'coin telegraph': 'post-content'
}

# def get_article_type
    
def get_article(self, url: str, class_: str, parse: bool=True):
    headers = {'User-Agent': r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as err:
        print ("Error",err)
    else:
        tree = lxml.html.fromstring(response.content)
        try:
            text = tree.find_class(class_)[0]

            article = [re.sub(r"(\xa0)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", '', str(paragraph.text_content())) for paragraph in text.xpath('p')]

        except IndexError:
            print("Bad class", url)
            return []

@staticmethod
def get_rss_feed(url: str, N: int) -> pd.DataFrame:
    news_feed = feedparser.parse(url) 

    #Flatten data
    df=pd.json_normalize(news_feed.entries)[['title', 'link', 'summary']]

    return df.iloc[-N:]

@staticmethod
def get_articles(url: str, class_: str, parse: bool=True, N: int=0):
    df = get_rss_feed(url, N)
    articles = [get_article(link, class_, parse) for link in df.link]
    return articles