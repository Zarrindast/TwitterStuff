terms = ["#prop16", "#proposition16", "#yesonprop16", "#noonprop16", "#noonproposition16", "#yesonproposition16", "#yeson16", "#noon16", "#CAprop16", "#CAproposition16"]
import twitterscraper
from twitterscraper import query_tweets

def function(term_in_quotes, num, output_in_quotes):
  terms = ["#prop16", "#proposition16", "#yesonprop16", "#noonprop16", "#noonproposition16", "#yesonproposition16", "#yeson16", "#noon16", "#CAprop16", "#CAproposition16"]

list_of_tweets = query_tweets("#prop16", 10)
file = open("tw_prop16.txt","w")
for tweet in list_of_tweets:
      file.write(str(tweet.text.encode('utf-8')))
file.close()

----------

pip install requests
pip install bs4
import requests
import bs4
from bs4 import BeautifulSoup

class TwitterHashTagPosts:

    def __init__(self, hashtag):
        self.hashtag = hashtag
        self.tweets = []
        self.url = "https://mobile.twitter.com/hashtag/" + self.hashtag.strip()

    def scrape_tweets(self):
        content = requests.get(self.url)
        soup = BeautifulSoup(content.text, "html.parser")
        tweet_divs = soup.select("#main_content")[0].select(".tweet")
        for tweet in tweet_divs:
            handle = tweet.find("div", {"class": "username"}).text.replace("\n", " ").strip()
            post = tweet.find("div", {"class": "tweet-text"}).text.replace("\n", " ").strip()
            self.tweets.append({handle: post})
        return self.tweets

x = TwitterHashTagPosts("prop16")
x.scrape_tweets()

y = ... etc

%pip install pymongo
import pymongo

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import datetime
from pymongo import MongoClient
import pymongo


INIT_URL = 'https://twitter.com/search?f=tweets&vertical=default&q={q}&l={lang}'
RELOAD_URL = 'https://twitter.com/i/search/timeline?f=tweets&vertical=' \
             'default&include_available_features=1&include_entities=1&' \
             'reset_error_state=false&src=typd&max_position={pos}&q={q}&l={lang}'


lang = 'en'
myUa = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
HEADER = {'User-Agent': myUa}


i = 0

def writeTweets(tweets, collection):
    newTweetRecords = []
    for tweet in tweets:
        try:
            if tweet.find("a", {"class" : "js-action-profile-promoted"}):
                continue

            text = tweet.find("p", {"class" : "tweet-text"}).get_text()
            date = tweet.find("span", {"class" : "_timestamp"})["data-time-ms"]
            tweetId = tweet['data-item-id']
            replyCount = tweetMetadata(tweet, "ProfileTweet-action--reply")
            retweetCount = tweetMetadata(tweet, "ProfileTweet-action--retweet")
            favoriteCount = tweetMetadata(tweet, "ProfileTweet-action--favorite")
            verified = False
            if tweet.find("span", {"class" : "Icon--verified"}) != None:
                verified = True
            tweetRecord = {"text" : text, "date" : date, "tweetId" : tweetId,
                           "replyCount": replyCount, "retweetCount": retweetCount,
                           "favoriteCount": favoriteCount, "verified" : verified}
            newTweetRecords.append(tweetRecord)
        except:
            print("Unable to process tweet")
        try:
            result = collection.insert_many(newTweetRecords, ordered=False)
            i += len(newTweetRecords)
        except pymongo.errors.BulkWriteError as e:
            panic = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
            if len(panic) > 0:
                print(e)


def tweetMetadata(tweet, divClass):
    dataBlock = tweet.find("div", {"class": divClass})
    data = dataBlock.find("span", {"class" : "ProfileTweet-actionCountForPresentation"}).get_text()
    if data == '':
        data = 0
    else:
        data = int(data)
    return data

def generateQuery(keywords, since, until):
    query = '{} since:{} until:{}'.format(keywords, since, until)
    query = query.replace(' ', '%20').replace('#', '%23').replace(':', '%3A')
    return query

def executeQuery(keywords, since, until, collection):
    query = generateQuery(keywords, since, until)
    url = INIT_URL.format(q=query, lang=lang)
    response = requests.get(url, headers=HEADER)
    soup = BeautifulSoup(response.text, 'lxml')
    tweets = soup.find_all("li", {"data-item-type": "tweet"})
    writeTweets(tweets, collection)
    next_pointer = soup.find("div", {"class": "stream-container"})["data-min-position"]
    counter = 0
    for i in range(100):
        #time.sleep(1)
        url = RELOAD_URL.format(q=query, lang=lang, pos = next_pointer)
        if response.status_code != 200:
            print(response.status_code)

        response = requests.get(url, headers=HEADER)
        try:
            json_resp = json.loads(response.text)
        except:
            print("Unable to process json response")
            print(response.text)
            return
        html = json_resp['items_html']
        soup = BeautifulSoup(html, 'lxml')
        tweets = soup.find_all("li", {"data-item-type": "tweet"})
        if len(tweets) == 0:
            print(soup)
            return
        writeTweets(tweets, collection)
        if (not json_resp['has_more_items']) and (json_resp["new_latent_count"] == 0):
            break
        next_pointer = json_resp['min_position']


if __name__ == '__main__':
    main()
