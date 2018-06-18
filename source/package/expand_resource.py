# Command line arguments
import argparse
ap = argparse.ArgumentParser()
ap.add_argument('resource_file', help='The path for the resource without tweets.')
ap.add_argument('consumer_key', help='Consumer key for the Twitter API')
ap.add_argument('consumer_secret', help='Consumer secret for the Twitter API')
ap.add_argument('access_token', help='Access key token for the Twitter API')
ap.add_argument('access_token_secret', help='Access token secret for the Twitter API')
args = ap.parse_args()

import os
import re
import math
import time
import string
import codecs
import twitter
import HTMLParser

import logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()])
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
logger.setLevel(logging.INFO)

from spacy.en import English
from common import camel_case_split


def main():
    """
    Download the tweets in the resource by their tweet IDs.
    """
    nlp = English()
    tweet_ids = set()
    tweet_cache = {}

    api = twitter.Api(consumer_key=args.consumer_key, consumer_secret=args.consumer_secret,
                      access_token_key=args.access_token, access_token_secret=args.access_token_secret)

    [sleeptime, resettime] = reset_sleep_time(api)

    with codecs.open(os.path.basename(args.resource_file) + '_extended', 'w', 'utf-8') as f_out:
        with codecs.open(args.resource_file, 'r', 'utf-8') as f_in:
            for line in f_in:
                try:
                    tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1, \
                    tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1 = \
                        line.strip().split('\t')

                    tweet1, sleeptime, resettime = sent_by_tweet_id(
                        tweet_ids, tweet_cache, api, sleeptime, resettime, nlp, tweet_id1)
                    tweet2, sleeptime, resettime = sent_by_tweet_id(
                        tweet_ids, tweet_cache, api, sleeptime, resettime, nlp, tweet_id2)

                    if tweet1 is not None and tweet2 is not None:
                        print >> f_out, '\t'.join((tweet_id1, tweet1, sf_pred1, pred1, sent1_a0, sent1_a1,
                                                   tweet_id2, tweet2, sf_pred2, pred2, sent2_a0, sent2_a1))

                except twitter.TwitterError as err:
                    if err.message == 'Rate limit exceeded':
                        time.sleep(sleeptime * 10)


def sent_by_tweet_id(tweet_ids, tweet_cache, api, sleeptime, resettime, nlp, tweet_id):

    # We didn't download this tweet yet
    if not tweet_id in tweet_ids:
        try:
            curr_tweet = api.GetStatus(tweet_id, include_entities=False)
            tweet_text = re.sub('\n+', '. ', HTMLParser.HTMLParser().unescape(curr_tweet.text))
            tweet_cache[tweet_id] = clean_tweet(' '.join([t.text for t in nlp(tweet_text)]),
                                                set([hashtag.text for hashtag in curr_tweet.hashtags]),
                                                set([url.url for url in curr_tweet.urls]),
                                                { u.screen_name : u.name for u in curr_tweet.user_mentions })
            logger.info('\t'.join((tweet_id, tweet_cache[tweet_id])))
            time.sleep(sleeptime)
            if time.time() >= resettime:
                sleeptime, resettime = reset_sleep_time(api)

        except twitter.TwitterError as err:
            error = str(err)

            # If the rate limit exceeded, this script should be stopped and resumed the next day
            if 'Rate limit exceeded' in error:
                raise

            # Other error - the tweet is not available :(
            logger.error('Error reading tweet id: {} : {}'.format(tweet_id, error))
            tweet_cache[tweet_id] = None

    return tweet_cache[tweet_id], sleeptime, resettime


def reset_sleep_time(api):
    """
    Sleep between API requests (from: https://gist.github.com/emaadmanzoor)
    :param api: twitter API
    :return: the sleep time and reset time
    """
    rate_limit_stats = api.GetRateLimitStatus()
    show_status_limits = rate_limit_stats['resources']['statuses']['/statuses/show/:id']
    hits_remaining = show_status_limits['remaining']
    reset_time = show_status_limits['reset']
    div = hits_remaining if hits_remaining > 0 else 1
    sleep_time = int(math.ceil((int(reset_time) - time.time()) * 1.0 / int(div)))
    logger.info('Sleeping {} seconds between API hits until {}'.format(sleep_time, reset_time))
    return sleep_time, reset_time


def clean_tweet(tweet, hashtags, urls, user_mentions):
    """
    Receives a tweet and removes the hashtags and urls
    :param tweet: the original tweet
    :return: the cleaned tweet
    """
    # Remove RT (retweet)
    tweet = re.sub(r'^RT [^\s]+\s?: ', '', tweet)

    # Remove "via something"
    tweet = re.sub(r'via\s?[^\s]*$', '', tweet)
    tweet = tweet.replace(u'\u2026', '...')

    tokens = tweet.split()
    cleaned_tokens = tokens

    # Remove URLS
    if cleaned_tokens[-1].startswith('ht'):
        cleaned_tokens = cleaned_tokens[:-1]

    cleaned_tokens = [token for token in cleaned_tokens
                      if token not in urls and 't.co' not in token and 'http' not in token]

    # Remove hashtags in the end of the sentence
    if len(hashtags) > 0:
        cleaned_tokens = [token for token in cleaned_tokens if token != '#']
        cleaned_tokens = [token for i, token in enumerate(cleaned_tokens) if token not in hashtags or
                  (len(cleaned_tokens) > i+1 and cleaned_tokens[i+1] not in hashtags and
                   len(re.sub('[{}]+'.format(''.join(string.punctuation)), '', cleaned_tokens[i+1])) > 1)]
        cleaned_tokens = [token if token not in hashtags else camel_case_split(token) for token in cleaned_tokens]

    # Replace mentions by names
    cleaned_tokens = [re.sub(r'^.?@', '', token) for token in cleaned_tokens]
    cleaned_tokens = [user_mentions.get(token, token) for token in cleaned_tokens]

    # Remove whitespaces before punctuations
    cleaned_tweet = re.sub(r'\s+([?.!,:;@_~$%])', r'\1', ' '.join(cleaned_tokens))
    cleaned_tweet = re.sub(r'\.\.\.$', '', cleaned_tweet)

    cleaned_tweet = re.sub(r"\sn\'t", r"n't", cleaned_tweet)
    cleaned_tweet = re.sub(r"\s\'s", r"'s", cleaned_tweet)

    cleaned_tweet = re.sub(r"(\s|^)\(\s+([^\)]+)\s+\)([?.!,:;@_~$%\s]|$)", r"\1(\2)\3", cleaned_tweet)
    cleaned_tweet = re.sub(r"(\s|^)\[\s+([^\]]+)\s+\]([?.!,:;@_~$%\s]|$)", r"\1[\2]\3", cleaned_tweet)
    cleaned_tweet = re.sub(r"(\s|^)\{\s+([^\}]+)\s+\}([?.!,:;@_~$%\s]|$)", r"\1{\2}\3", cleaned_tweet)

    cleaned_tweet = re.sub(r"(\s|^)\'\s+([^\']+)\s+\'([?.!,:;@_~$%\s]|$)", r"\1'\2'\3", cleaned_tweet)
    cleaned_tweet = re.sub(r'(\s|^)"\s+([^"]+)\s+"([?.!,:;@_~$%\s]|$)', r'\1"\2"\3', cleaned_tweet)

    return cleaned_tweet


if __name__ == '__main__':
    main()