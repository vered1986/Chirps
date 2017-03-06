"""
author: Vered Shwartz

Receives a file with positive instances, and samples negatives instances, such that they are from different dates and
do not share the same predicate or arguments.
"""
from get_corefering_predicates import *


def main():
    """
    Receives a file with positive instances, and samples negatives instances, such that they are from different dates
    and do not share the same predicate or arguments.
    """
    args = docopt("""Receives a file with positive instances, and samples negatives instances, such that they are from
    different dates and do not share the same predicate or arguments.

    Usage:
        create_negative_sampling_svo_instances.py <positive_instances_file> <negative_instances_file> <actions_log_file> <ratio_neg_pos>

        <positive_instances_file> = the file containing the positive propositions
        <negative_instances_file> = where to save the negative instances.
        <actions_log_file> = operations needed to be performed on the tweets to re-create the negative samples.
        <ratio_neg_pos> = the ratio of negative to positive to generate.
    """)

    positive_instances_file = args['<positive_instances_file>']
    negative_instances_file = args['<negative_instances_file>']
    actions_log_file = args['<actions_log_file>']
    ratio_neg_pos = int(args['<ratio_neg_pos>'])

    log = codecs.open(actions_log_file, 'w', 'utf-8')

    # Read the positive examples
    with codecs.open(positive_instances_file, 'r', 'utf-8') as f_in:
        positive = [tuple(line.strip().split('\t')) for line in f_in]

    # Generate negative examples
    negative = codecs.open(negative_instances_file, 'w', 'utf-8')

    for pos in positive:

        date, tweet_id1, sent1, sf_pred1, pred1, sent1_a0, sent1_a1, \
        tweet_id2, sent2, sf_pred2, pred2, sent2_a0, sent2_a1 = pos

        print >> log, 'Current positive instance: ' + \
                      "tweet_id1 = '%s', sf_pred1 = '%s', pred1 = '%s', sent1_a0 = '%s', sent1_a1 = '%s', " % \
                      (tweet_id1, sf_pred1.replace("'", '"'),  pred1.replace("'", '"'),
                       sent1_a0.replace("'", '"'), sent1_a1.replace("'", '"')) + \
                      "tweet_id2 = '%s', sf_pred2 = '%s', pred2 = '%s', sent2_a0 = '%s', sent2_a1 = '%s'" % \
                      (tweet_id2, sf_pred2.replace("'", '"'), pred2.replace("'", '"'),
                       sent2_a0.replace("'", '"'), sent2_a1.replace("'", '"'))

        # Replace the predicate
        neg1 = [(tid1, s1, sf_p1, p1, s1_a0, s1_a1, tid2, s2, sf_p2, p2, s2_a0, s2_a1) for
                (d, tid1, s1, sf_p1, p1, s1_a0, s1_a1, tid2, s2, sf_p2, p2, s2_a0, s2_a1) in positive
                if d != date and not is_aligned_preds(pred1, p2) and not is_eq_preds(pred1, p2)]

        if len(neg1) > 0:

            curr_negative_indices = np.random.choice(range(len(neg1)), size=ratio_neg_pos, replace=False)
            curr_negatives = [neg1[index] for index in curr_negative_indices]
            i = 1

            for curr_negative in curr_negatives:

                _, _, _, _, _, _, tid2, s2, sf_p2, p2, s2_a0, s2_a1 = curr_negative

                # Replace the predicate in sent2 and in pred2
                pred2_in_sent = sf_pred2.replace('{a0}', sent2_a0).replace('{a1}', sent2_a1)
                p2_in_sent = sf_p2.replace('{a0}', sent2_a0).replace('{a1}', sent2_a1)

                # There are characters between the predicate and arguments: replace only the predicate
                if pred2_in_sent not in sent2:
                    if (pred2.startswith('{a0}') or pred2.startswith('{a1}')) and \
                            (pred2.endswith('{a0}') or pred2.endswith('{a1}')):
                        pred2_in_sent = sf_pred2.replace('{a0}', '').replace('{a1}', '').strip()
                        p2_in_sent = sf_p2.replace('{a0}', '').replace('{a1}', '').strip()

                    else:
                        continue

                print >> log, '%d)' % i
                new_sent2 = sent2.replace(pred2_in_sent, p2_in_sent)
                print >> log, "new_sent2 = sent2.replace('%s', '%s')" % (pred2_in_sent.replace("'", '"'),
                                                                         p2_in_sent.replace("'", '"'))

                new_pred2 = p2
                new_sf_pred2 = sf_p2
                print >> log, "new_pred2 = '%s'" % p2.replace("'", '"')
                print >> log, "new_sf_pred2 = '%s'" % sf_p2.replace("'", '"')

                neg = tweet_id1, sent1, sf_pred1, pred1, sent1_a0, sent1_a1, \
                      tweet_id2, new_sent2, new_sf_pred2, new_pred2, sent2_a0, sent2_a1

                i += 1
                print >> negative, '\t'.join(neg)

    negative.close()
    log.close()


if __name__ == '__main__':
    main()