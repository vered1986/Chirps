import codecs

from docopt import docopt
from shutil import copyfile
from collections import Counter


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
    copyfile(resource_file, repository_dir + '/resource/instances.tsv')
    print 'Copied instances file'

    # Read the resource
    with codecs.open(resource_file, 'r', 'utf-8') as f_in:
        resource = [tuple(line.strip().split('\t')) for line in f_in]

    # Generate the types file
    types = ['###'.join(sorted([pred1, pred2])) for (tweet_id1, sf_pred1, pred1, sent1_a0, sent1_a1,
                                                     tweet_id2, sf_pred2, pred2, sent2_a0, sent2_a1) in resource]
    types = Counter(types)

    with codecs.open(repository_dir + '/resource/rules.tsv', 'w', 'utf-8') as f_out:
        for key, count in types.most_common():
            p1, p2 = key.split('###')
            print >> f_out, '\t'.join((p1, p2, str(count)))

    print 'Copied types file'


if __name__ == '__main__':
    main()
