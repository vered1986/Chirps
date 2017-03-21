import sys
import time
import codecs
import datetime

sys.path.append('../')

from docopt import docopt
from common.common import *
from TwitterSearch import *


def main():
    """
    Retrieve news tweet using Twitter Search API with filter for news.
    Important note: we downloaded TwitterSearch from https://github.com/ckoepp/TwitterSearch and added the
    filter to the search URL!
    This filter retrieves tweets from the requested date (or from now if left empty) that contain links to news
    web sites.
    """

    args = docopt("""Retrieve news tweet using Twitter Search API with filter for news.
        Important note: we downloaded TwitterSearch from https://github.com/ckoepp/TwitterSearch and added the
        filter to the search URL!
        This filter retrieves tweets from the requested date (or from now if left empty) that contain links to news
        web sites.

        This script will save the tweets in a file named by the date they were created at.

        Usage: get_news_tweets_stream.py <consumer_key> <consumer_secret> <access_token> <access_token_secret> [<until>]

        Argumments:
            consumer_key  Consumer key for the Twitter API
            consumer_secret  Consumer secret for the Twitter API
            access_token  Access key token for the Twitter API
            access_token_secret  Access token secret for the Twitter API
            until  (Optional): date in the format YYYY/MM/dd. Retrieve tweets only until this date.
            If this argument is not specified, it will retrieve current tweets.
            The Search API only supports up to one week ago.
    """)

    consumer_key = args['<consumer_key>']
    consumer_secret = args['<consumer_secret>']
    access_token = args['<access_token>']
    access_token_secret = args['<access_token_secret>']

    tso = TwitterSearchOrder()
    tso.set_keywords(['.'])
    tso.set_language('en')

    # Set until date
    if args['<until>']:
        year, month, day = map(int, args['-until'].split('/'))
        out_tweet_file = 'news_stream/tweets/%d_%02d_%02d' % (year, month, day - 1)
        tso.set_until(datetime.date(year, month, day))
    else:
        out_tweet_file = 'news_stream/tweets/' + time.strftime('%Y_%m_%d')


    sleep_for = 10
    last_amount_of_queries = 0

    ts = TwitterSearch(consumer_key=consumer_key, consumer_secret=consumer_secret,
                       access_token=access_token, access_token_secret=access_token_secret)

    tweets = set()

    with codecs.open(out_tweet_file, 'w', 'utf-8') as f_out:

        # Stop this manually
        while True:
            try:

                # Get the next batch of tweets
                for tweet in ts.search_tweets_iterable(tso):
                    text = clean_tweet(tweet['text'].encode(sys.getdefaultencoding(), 'ignore').replace('\n', ' '))

                    if not text in tweets:
                        print >> f_out, '\t'.join((tweet['created_at'], str(tweet['id']), tweet['user']['screen_name'], text))
                        tweets.add(text)

                    current_amount_of_queries = ts.get_statistics()[0]

                    # Handle API rate limit
                    if not last_amount_of_queries == current_amount_of_queries:
                        last_amount_of_queries = current_amount_of_queries
                        time.sleep(sleep_for)

            except TwitterSearchException as e:
                time.sleep(sleep_for)
                pass

    
if __name__ == '__main__':
    main()