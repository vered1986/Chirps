import os
import sys

sys.path.append('../common')

from common import *
from docopt import docopt
from spacy.en import English


def main():
    """
    Download the tweets in the resource by their tweet IDs.
    """

    args = docopt("""Download the tweets in the resource by their tweet IDs.

        Usage: expand_resource.py --resource_file=<resource_file> --consumer_key=<consumer_key>
        --consumer_secret=<consumer_secret> --access_token=<access_token> --access_token_secret=<access_token_secret>

        --resource_file         The path for the resource without tweets.
        --consumer_key          Consumer key for the Twitter API
        --consumer_secret       Consumer secret for the Twitter API
        --access_token          Access key token for the Twitter API
        --access_token_secret   Access token secret for the Twitter API
    """)

    nlp = English()

    resource_file = args['--resource_file']
    consumer_key = args['--consumer_key']
    consumer_secret = args['--consumer_secret']
    access_token = args['--access_token']
    access_token_secret = args['--access_token_secret']

    # Read the resource without tweets
    resource = load_resource(resource_file)

    # Get the tweet IDs
    tweet_ids = get_tweet_ids(resource)

    # Expand tweets
    try:
        tweet_by_id = get_tweets(tweet_ids, consumer_key, consumer_secret, access_token, access_token_secret, nlp)

    except twitter.TwitterError as err:
        print 'An error occurred:', str(err), 'If your rate limit exceeded, try again later. ' + \
                                              'All the tweets you already downloaded are saved in a temporary file, ' + \
                                              'and the script will resume from where it stopped.'
        exit

    # Expand the resource
    expanded_resource = expand_resource(resource, tweet_by_id)

    if not os.path.exists('expanded'):
        os.makedirs('expanded')

    save_to_file(expanded_resource, "expanded/resource.tsv")


if __name__ == '__main__':
    main()