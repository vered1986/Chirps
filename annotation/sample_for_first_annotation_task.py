import codecs
import random

import numpy as np

from docopt import docopt
from collections import defaultdict


def main():
    """
    Sample from the resource according to score (number of occurrences * number of different days),
    NUM_INS instances from each of the NUM_BIN bins.
    """

    args = docopt("""Sample from the resource according to score (number of occurrences * number of different days),
    NUM_INS instances from each of the NUM_BIN bins.

        Usage: sample_for_first_annotation_task.py <resource_dir> <num_ins> <num_bin> <out_file>

        <resource_dir>    The resource directory, containing the rules and instances files.
        <num_ins>         Number of instances to sample from each bin.
        <num_bin>         Number of bins.
        <out_file>        Batch instances csv out file.
    """)

    resource_dir = args['<resource_dir>']
    num_instances = int(args['<num_ins>'])
    num_bins = int(args['<num_bin>'])
    out_file = args['<out_file>']

    # Open the types file
    with codecs.open(resource_dir + '/rules.tsv', 'r', 'utf-8') as f_in:
        types = [tuple(line.strip().split('\t')) for line in f_in]

    # Filter types with too few instances to annotate
    types = [(p1, p2, count, days) for (p1, p2, count, days) in types if int(count) >= 5]
    print 'Sampling from %d types with at least 5 instances' % len(types)

    # Split to num_bin bins. Each bin contains all the items that have higher scores
    # than the low threshold of the bin. The last bin should contain all the resource (as
    # long as there at least 5 instances).
    scores = [int(count) * int(days) for (p1, p2, count, days) in types]
    score_bins = np.flipud(np.linspace(5, 250, num=num_bins+1))
    bins = [[item for j, item in enumerate(types) if scores[j] >= score_bins[i+1]] for i in range(num_bins)]
    print 'Bins and number of items:', [(score_bins[bin+1], len(bins[bin])) for bin in range(num_bins)]

    # Sample num_ins from each bin
    samples = [random.sample(curr_bin, num_instances) for curr_bin in bins]

    type_to_bin = defaultdict(list)
    [type_to_bin['###'.join(sorted([p1, p2]))].append(int(i + 1)) for i, bin in enumerate(samples)
     for (p1, p2, count, days) in bin]

    # Open the instances file
    with codecs.open(resource_dir + '/instances.tsv', 'r', 'utf-8') as f_in:
        curr_instances = [tuple(line.strip().split('\t')) for line in f_in]

    instances_by_type = defaultdict(list)
    [instances_by_type['###'.join(sorted([p1, p2]))].append((sf_p1.replace('"', "''"), s1_a0.replace('"', "''"),
                                                             s1_a1.replace('"', "''"), sf_p2.replace('"', "''"),
                                                             s2_a0.replace('"', "''"), s2_a1.replace('"', "''")))
     for (tid1, sf_p1, p1, s1_a0, s1_a1, tid2, sf_p2, p2, s2_a0, s2_a1) in curr_instances]

    # Sample 5 instances for each type and generate annotation instances
    with codecs.open(out_file, 'w', 'utf-8') as f_out:

        # Header
        print >> f_out, '"' + '","'.join(('p1', 'p2', 'bin', 'inst1_1', 'inst1_2', 'inst2_1', 'inst2_2',
                                          'inst3_1', 'inst3_2', 'inst4_1', 'inst4_2', 'inst5_1', 'inst5_2')) + '"'

        for type, bin_lst in type_to_bin.iteritems():

            p1, p2 = type.split('###')
            curr_bins = '-'.join(map(str, bin_lst))
            sample_instances = random.sample(instances_by_type[type], 5)

            sample_instances = [(sf_p1.replace('{a0}', "<font color='#d95f02'>%s</font>" % s1_a0).
                                 replace('{a1}', "<font color='#7570b3'>%s</font>" % s1_a1),
                                 sf_p2.replace('{a0}', "<font color='#d95f02'>%s</font>" % s2_a0).
                                 replace('{a1}', "<font color='#7570b3'>%s</font>" % s2_a1))
                                for (sf_p1, s1_a0, s1_a1, sf_p2, s2_a0, s2_a1) in sample_instances]

            sample_instances = [item for lst in sample_instances for item in lst]

            print >> f_out, '"' + '","'.join([p1.replace('"', "''"), p2.replace('"', "''"), curr_bins] +
                                             sample_instances) + '"'



if __name__ == '__main__':
    main()
