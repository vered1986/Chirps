import math
import pandas

import numpy as np

from docopt import docopt
from collections import defaultdict
from sklearn.metrics import cohen_kappa_score


def main():
    """
    Analyze the results of the first annotation task: annotating rule types in different confidence bins.
    """

    args = docopt("""Analyze the results of the first annotation task: annotating rule types in different confidence bins.

        Usage: analyze_first_task_results.py <batch_result_file>

        <batch_result_file>    The MTurk batch results file
    """)

    batch_result_file = args['<batch_result_file>']

    # Load the results
    workers, results, keys_by_bin = load_results(batch_result_file)

    # Compute agreement between workers that answered at least 5 HITs
    kappa, workers_to_remove = cohens_kappa(results, workers)
    print 'Cohen\'s kappa=%.2f' % kappa
    num_hits_removed = 0

    for key, key_worker_answers in results.iteritems():
        for worker in key_worker_answers.keys():
            if worker in workers_to_remove:
                num_hits_removed += len(key_worker_answers[worker])
                key_worker_answers.pop(worker, None)

    print 'Number of workers removed: %d, total HITs removed: %d' % (len(workers_to_remove), num_hits_removed)
    print

    # Compute accuracy for each bin
    # keys_by_bin = { 1 : keys_by_bin[1] + keys_by_bin[2], 2 : keys_by_bin[3], 3 : keys_by_bin[4] }

    for bin in keys_by_bin.keys():

        curr_results = { key : results[key] for key in keys_by_bin[bin] }
        answers = compute_majority_gold(curr_results).values()
        print 'Accuracy of bin %d: %.3f' % (bin, np.sum(answers) * 100.0 / len(curr_results))

    print


def compute_majority_gold(results):
    """
    Get the TRUE items that the annotators agreed they are true
    :param results: key to worker answers dictionary
    :return: key to majority label dictionary
    """
    majority_gold = { key : np.argmax(np.bincount([1 if annotations[0] else 0 for worker, annotations
                                                   in results[key].iteritems()]))
                      for key in results.keys() }

    return majority_gold


def load_results(result_file):
    """
    Load the batch results from the CSV
    :param result_file: the batch results CSV file from MTurk
    :return: the workers and the answers
    """
    worker_answers = {}
    keys_by_bin = defaultdict(list)
    workers = set()
    table = pandas.read_csv(result_file, dtype={'Input.tweet_id2': str})

    for index, row in table.iterrows():

        hit_id = row['HITId']
        worker_id = row['WorkerId']

        # Input fields
        p1 = row['Input.p1']
        p2 = row['Input.p2']
        bins = row['Input.bin']

        # Answer fields
        answer = any([row['Answer.ans%d' % (i + 1)] == 'yes' for i in range(5)])
        comment = row['Answer.comment']

        key = (p1, p2)

        bins = map(int, bins.split('-'))

        for bin in bins:
            keys_by_bin[bin].append(key)

        if key not in worker_answers.keys():
            worker_answers[key] = {}

        workers.add(worker_id)

        worker_answers[key][worker_id] = (answer, comment)

    return workers, worker_answers, keys_by_bin


def cohens_kappa(results, workers):
    """
    Compute Cohen's Kappa on all workers that answered at least 5 HITs
    :param results:
    :return:
    """
    answers_per_worker = { worker_id : { key : results[key][worker_id] for key in results.keys()
                                         if worker_id in results[key] }
                           for worker_id in workers }
    answers_per_worker = { worker_id : answers for worker_id, answers in answers_per_worker.iteritems()
                           if len(answers) >= 5 }
    curr_workers = answers_per_worker.keys()
    worker_pairs = [(worker1, worker2) for worker1 in curr_workers for worker2 in curr_workers if worker1 != worker2]

    label_index = { True : 1, False : 0 }
    pairwise_kappa = { worker_id : { } for worker_id in answers_per_worker.keys() }

    # Compute pairwise Kappa
    for (worker1, worker2) in worker_pairs:

        mutual_hits = set(answers_per_worker[worker1].keys()).intersection(set(answers_per_worker[worker2].keys()))
        mutual_hits = set([hit for hit in mutual_hits if not pandas.isnull(hit)])

        if len(mutual_hits) >= 5:

            worker1_labels = np.array([label_index[answers_per_worker[worker1][key][0]] for key in mutual_hits])
            worker2_labels = np.array([label_index[answers_per_worker[worker2][key][0]] for key in mutual_hits])
            curr_kappa = cohen_kappa_score(worker1_labels, worker2_labels)

            if not math.isnan(curr_kappa):
                pairwise_kappa[worker1][worker2] = curr_kappa
                pairwise_kappa[worker2][worker1] = curr_kappa

    # Remove worker answers with low agreement to others
    workers_to_remove = set()

    for worker, kappas in pairwise_kappa.iteritems():
        if np.mean(kappas.values()) < 0.1:
            print 'Removing %s' % worker
            workers_to_remove.add(worker)

    kappa = np.mean([k for worker1 in pairwise_kappa.keys() for worker2, k in pairwise_kappa[worker1].iteritems()
                     if not worker1 in workers_to_remove and not worker2 in workers_to_remove])

    # Return the average
    return kappa, workers_to_remove


if __name__ == '__main__':
    main()