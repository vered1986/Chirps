"""
author: Vered Shwartz

Creates a script that receives the dataset without tweets and downloads the tweets from Twitter API
"""
from common import *
from docopt import docopt


def main():
    """
    Receives the dataset and the negative instances log file, and creates a script to create the
    dataset, including downloading tweets from the Twitter API.
    """
    args = docopt("""Receives the dataset and the negative instances log file, and creates a script to create the
    dataset, including downloading tweets from the Twitter API.

    Usage:
        create_download_dataset_script.py <dataset_file> <negative_instances_log_file> <out_script_file>

        <dataset_file> = the dataset file, with tweets.
        <negative_instances_log_file> = operations needed to be performed on the tweets to re-create the negative samples.
        <out_script_file> = where to save the script.
    """)

    dataset_file = args['<dataset_file>']
    negative_instances_log_file = args['<negative_instances_log_file>']
    out_script_file = args['<out_script_file>']

    f_out = codecs.open(out_script_file, 'w', 'utf-8')

    print >> f_out, 'import os'
    print >> f_out, 'import sys'
    print >> f_out, 'import random'
    print >> f_out, 'import codecs'
    print >> f_out, 'import argparse'
    print >> f_out, '\n'
    print >> f_out, 'from common import *'
    print >> f_out, 'from spacy.en import English'
    print >> f_out, '\n'

    print >> f_out, 'nlp = English()'
    print >> f_out, '\n'

    # Arguments: consumer_key, consumer_secret, access_token, access_token_secret
    print >> f_out, '# Get arguments to access Twitter API'
    print >> f_out, 'parser = argparse.ArgumentParser()'
    print >> f_out, "parser.add_argument('--dataset_file', help='The dataset file without tweets', required=True)"
    print >> f_out, "parser.add_argument('--consumerkey', help='The Twitter app consumer key', required=True)"
    print >> f_out, "parser.add_argument('--consumersecret', help='The Twitter app consumer secret', required=True)"
    print >> f_out, "parser.add_argument('--accesstoken', help='The Twitter app API token', required=True)"
    print >> f_out, "parser.add_argument('--accesstokensecret', help='The Twitter app API token secret', required=True)"
    print >> f_out, "args = parser.parse_args()"
    print >> f_out, '\n'

    # Read the dataset with tweets
    dataset = load_dataset(dataset_file)

    print >> f_out, '# Read the dataset without tweets'
    print >> f_out, 'dataset = load_dataset(args.dataset_file)'
    print >> f_out, '\n'

    print >> f_out, '# Get the tweet ids'
    print >> f_out, 'tweet_ids = get_tweet_ids(dataset)'
    print >> f_out, '\n'

    print >> f_out, '# Expand tweets'
    print >> f_out, 'try:'
    print >> f_out, '\ttweet_by_id = get_tweets(tweet_ids, args.consumerkey, args.consumersecret, ' + \
                    'args.accesstoken, args.accesstokensecret, nlp)'
    print >> f_out, 'except twitter.TwitterError as err:'
    print >> f_out, '\tprint "An error occurred:", str(err), "If your rate limit exceeded, try again later. ' + \
                    'All the tweets you already downloaded are saved in a temporary file, and the script will resume ' + \
                    'from where it stopped."'
    print >> f_out, '\texit'
    print >> f_out, '\n'

    tweet_by_id = { tweet_id1 : sent1 for (tweet_id1, sent1, sf_pred1, pred1, sent1_a0, sent1_a1,
                                           tweet_id2, sent2, sf_pred2, pred2, sent2_a0, sent2_a1, label)
                    in dataset }
    tweet_by_id.update({ tweet_id2 : sent2 for (tweet_id1, sent1, sf_pred1, pred1, sent1_a0, sent1_a1,
                                                tweet_id2, sent2, sf_pred2, pred2, sent2_a0, sent2_a1, label)
                         in dataset })

    print >> f_out, '# Positive instances'
    print >> f_out, "pos = [item for item in dataset if item[-1] == 'True']"
    print >> f_out, '\n'

    print >> f_out, "pos_expanded = expand_positive(pos, tweet_by_id)"
    print >> f_out, '\n'

    # Read the negative instances log
    curr_positive = None

    with codecs.open(negative_instances_log_file, 'r', 'utf-8') as f_in:
        lines = [line.strip() for line in f_in]

    print >> f_out, '# Negative instances'
    print >> f_out, 'neg = []'

    i = 0
    while i < len(lines):

        line = lines[i]
        print >> f_out, '\n'

        if line.startswith('Current positive instance: '):

            # Get the positive instance parameters
            tweet_id1 = re.search(r"tweet_id1 = '([^']+)'", line).group(1)
            sf_pred1 = re.search(r"sf_pred1 = '([^']+)'", line).group(1)
            pred1 = re.search(r" pred1 = '([^']+)'", line).group(1)
            sent1_a0 = re.search(r"sent1_a0 = '([^']+)'", line).group(1)
            sent1_a1 = re.search(r"sent1_a1 = '([^']+)'", line).group(1)

            tweet_id2 = re.search(r"tweet_id2 = '([^']+)'", line).group(1)
            sf_pred2 = re.search(r"sf_pred2 = '([^']+)'", line).group(1)
            pred2 = re.search(r" pred2 = '([^']+)'", line).group(1)
            sent2_a0 = re.search(r"sent2_a0 = '([^']+)'", line).group(1)
            sent2_a1 = re.search(r"sent2_a1 = '([^']+)'", line).group(1)

            curr_positive = (tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1,
                             tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1)

            print >> f_out, "curr_positive = ('%s', tweet_by_id['%s'], '%s', '%s', '%s', '%s', " \
                            "'%s', tweet_by_id['%s'], '%s', '%s', '%s', '%s')" % \
                            (tweet_id1, tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1,
                             tweet_id2, tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1)

            print >> f_out, 'tweet_id1, sent1, sf_pred1, pred1, sent1_a0, sent1_a1, ' + \
                            'tweet_id2, sent2, sf_pred2, pred2, sent2_a0, sent2_a1 = curr_positive'

            i += 1

        # Negative instance
        elif re.match('^[1-4]\)', line):

            # First line: new_sent2
            print >> f_out, lines[i + 1]

            # Second line: new_pred2
            print >> f_out, lines[i + 2]

            # Third line: new_sf_pred2
            print >> f_out, lines[i + 3]

            print >> f_out, 'neg.append((tweet_id1, sent1, sf_pred1, pred1, sent1_a0, sent1_a1, ' + \
                            'tweet_id2, new_sent2, new_sf_pred2, new_pred2, sent2_a0, sent2_a1))'

            i += 4

    print >> f_out, '\n'

    # Write to file
    print >> f_out, '\n'
    print >> f_out, '# Write to files'
    print >> f_out, 'dataset_expanded = pos_expanded + neg'
    print >> f_out, '\n'

    print >> f_out, 'if not os.path.exists("expanded"):\n\tos.makedirs("expanded")'
    print >> f_out, '\n'
    print >> f_out, 'save_to_file(dataset_expanded, "expanded/dataset.tsv")'
    print >> f_out, '\n'

    f_out.close()


if __name__ == '__main__':
    main()