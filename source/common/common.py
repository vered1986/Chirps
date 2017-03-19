"""
author: Vered Shwartz

Functions to get tweets from the Twitter API and expand the dataset
Twitter code is adapted from: https://gist.github.com/emaadmanzoor
"""
import re
import os
import math
import time
import codecs

import twitter


def get_tweets(tweet_ids, consumer_key, consumer_secret, access_token, access_token_secret, nlp):
    """
    Expands tweets from Twitter
    :param tweet_ids: the list of tweet IDs to expand
    :return: a dictionary of tweet ID to tweet text
    """

    # Save tweets in a temporary file, in case the script stops working and re-starts
    tweets = {}
    if os.path.exists('tweet_temp'):
        with codecs.open('tweet_temp', 'r', 'utf-8') as f_in:
            lines = [tuple(line.strip().split('\t')) for line in f_in]
            tweets = { tweet_id : tweet for (tweet_id, tweet) in lines }

    api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token,
                      access_token_secret=access_token_secret)

    [sleeptime, resettime] = reset_sleep_time(api)

    with codecs.open('tweet_temp', 'a', 'utf-8') as f_out:

        for tweet_id in tweet_ids:

            # We didn't download this tweet yet
            if not tweet_id in tweets:
                try:
                    curr_tweet = api.GetStatus(tweet_id, include_entities=False)
                    tweets[tweet_id] = clean_tweet(' '.join([t.lower_ for t in nlp(curr_tweet.text)]))

                except twitter.TwitterError as err:
                    error = str(err)

                    # If the rate limit exceeded, this script should be stopped and resumed the next day
                    if 'Rate limit exceeded' in error:
                        raise

                    # Other error - the tweet is not available :(
                    print 'Error reading tweet id:', tweet_id, ':', error
                    tweets[tweet_id] = 'TWEET IS NOT AVAILABLE'

                print >> f_out, '\t'.join((tweet_id, tweets[tweet_id]))

                time.sleep(sleeptime)
                if time.time() >= resettime:
                    [sleeptime, resettime] = reset_sleep_time(api)

    return tweets


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
    sleep_time = int(math.ceil((int(reset_time) - time.time()) * 1.0 / int(hits_remaining))) if hits_remaining > 0 else 5
    print 'Sleeping', sleep_time, 'seconds between API hits until', reset_time
    return sleep_time, reset_time


def load_resource(resource_file):
    """
    Load a resource from a file
    :param resource_file: the resource file
    :return: the resource
    """
    with codecs.open(resource_file, 'r', 'utf-8') as f_in:
        resource = [tuple(line.strip().split('\t')) for line in f_in]

    return resource


def get_tweet_ids(resource):
    """
    Returns all the tweet IDs in the resource
    :param resource: the resource
    :return: all the tweet IDs in the resource
    """
    tweet_ids = set([tweet_id1 for (tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1,
                                    tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1) in resource] + \
                [tweet_id2 for (tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1,
                                tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1) in resource])

    return tweet_ids


def expand_resource(resource, sent_by_tweet_id):
    """
    Add the tweets to the resource
    :param resource: the original resource (without tweets)
    :param sent_by_tweet_id: dictionary of tweet by tweet ID
    :return: the expanded resource (with tweets)
    """
    expanded_resource = [(tweet_id1, sent_by_tweet_id[tweet_id1], sf_pred1, pred1, sent1_a0, sent1_a1,
                         tweet_id2, sent_by_tweet_id[tweet_id2], sf_pred2, pred2, sent2_a0, sent2_a1)
                        for (tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1,
                             tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1) in resource]

    return expanded_resource


def save_to_file(dataset, dataset_file):
    """
    Recives a dataset (list of tuples) and a file name and saves the dataset in a tab-separated file.
    :param dataset: list of tuples
    :param dataset_file: file name
    :return:
    """
    with codecs.open(dataset_file, 'w', 'utf-8') as f_out:
        for item in dataset:
            print >> f_out, '\t'.join(item)


def clean_tweet(tweet):
    """
    Receives a tweet and removes the hashtags and urls
    :param tweet: the original tweet
    :return: the cleaned tweet
    """

    # Retweet
    tweet = tweet.lower()
    tweet = re.sub(r'^rt [^\s]+\s?: ', '', tweet)

    tokens = tweet.split()
    cleaned_tokens = []

    for token in reversed(tokens):

        # Hashtag
        if token.startswith('#'):

            # If it is in the end of a sentence / followed only by other hashtags or urls - remove it.
            # Else, the hashtag is not in the end of a sentence. Convert it to a regular text, e.g.:
            # "#SyrianRefugees should not be allowed. It doesn't take a rocket scientist to figure that out..." =>
            # "Syrian refugees should not be allowed. It doesn't take a rocket scientist to figure that out..."
            if len(cleaned_tokens) > 0:
                cleaned_tokens.append(camel_case_split(token))

            else:
                continue

        # URL - remove
        elif 't.co' in token or 'http' in token:
            continue

        # Mention - remove the @ and use it as a name
        elif token.startswith('@'):
            cleaned_tokens.append(token[1:].lower())

        # normal word
        else:
            cleaned_tokens.append(token.lower())

    return ' '.join(reversed(cleaned_tokens))


def camel_case_split(hashtag):
    """
    Convert camel case to regular text (for hashtags)
    :param hashtag:
    :return:
    """
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', hashtag[1:])
    return ' '.join([m.group(0).lower() for m in matches])