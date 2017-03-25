import codecs

from docopt import docopt
from collections import Counter, defaultdict


def main():
    """
    Package the resource: get instances file and generate two files: instances and types.
    """

    args = docopt("""Package the resource: get instances file and generate two files: instances and types.

        Usage: package_resource.py <resource_file> <repository_dir>

        <resource_file>         The path for the resource.
        <repository_dir>        The github repository directory.
    """)

    resource_file = args['<resource_file>']
    repository_dir = args['<repository_dir>']

    # Copy the instances file to the github directory
    with codecs.open(resource_file, 'r', 'utf-8') as f_in:
        resource = [tuple(line.strip().split('\t')) for line in f_in]

    with codecs.open(repository_dir + '/instances.tsv', 'w', 'utf-8') as f_out:
        for item in resource:
            print >> f_out, '\t'.join(item[1:])

    print 'Copied instances file'

    # Generate the types file
    types = ['###'.join(sorted([pred1, pred2])) for (date, tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1,
                                                     tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1) in resource]
    types = Counter(types)

    types_by_date = defaultdict(set)
    [types_by_date['###'.join(sorted([pred1, pred2]))].add(date)
     for (date, tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1, tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1) in resource]

    # Give more importance to rules that occurred in more than one day
    types_with_scores = [(key, count * (1 + len(types_by_date[key]) * 1.0 / len(types_by_date)))
                         for key, count in types.most_common()]
    types_with_scores = sorted(types_with_scores, key=lambda x: x[1], reverse=True)

    with codecs.open(repository_dir + '/rules.tsv', 'w', 'utf-8') as f_out:
        for key, score in types_with_scores:
            p1, p2 = key.split('###')
            print >> f_out, '\t'.join((p1, p2, str(types[key]), str(len(types_by_date[key]))))

    print 'Copied types file'


if __name__ == '__main__':
    main()
