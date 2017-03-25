import os
import codecs
import random

from docopt import docopt
from collections import defaultdict


def main():
    """
    Sample from the top K of each day and create batch instances.
    """

    args = docopt("""Sample from the top K of each day and create batch instances.

        Usage: sample_for_second_annotation_task.py <k> <num_instances> <out_file>

        <k>               k (as in top k)
        <num_instances>   How many instances from each day.
        <out_file>        Batch instances csv out file.
    """)

    k = int(args['<k>'])
    num_instances = int(args['<num_instances>'])
    out_file = args['<out_file>']

    types = defaultdict(list)
    instances_by_type = defaultdict(list)

    for day in os.listdir('.'):
        if os.path.isdir(day):

            # Open the types file and sample 20 types out of the top 100
            with codecs.open(day + '/rules.tsv', 'r', 'utf-8') as f_in:
                curr_top_k = [tuple(line.strip().split('\t')) for line in f_in][:k]

            sample_types = random.sample(curr_top_k, num_instances)
            [types['###'.join(sorted([p1, p2]))].append(int(day)) for (p1, p2, count, days) in sample_types]

            # Open the instances file
            with codecs.open(day + '/instances.tsv', 'r', 'utf-8') as f_in:
                curr_instances = [tuple(line.strip().split('\t')) for line in f_in]

            [instances_by_type['###'.join(sorted([p1, p2]))].append((sf_p1.replace('"', "''"), s1_a0.replace('"', "''"),
                                                                     s1_a1.replace('"', "''"), sf_p2.replace('"', "''"),
                                                                     s2_a0.replace('"', "''"), s2_a1.replace('"', "''")))
             for (tid1, sf_p1, p1, s1_a0, s1_a1, tid2, sf_p2, p2, s2_a0, s2_a1) in curr_instances]

    # Sample 5 instances for each type and generate annotation instances
    with codecs.open(out_file, 'w', 'utf-8') as f_out:

        # Header
        print >> f_out, '"' + '","'.join(('p1', 'p2', 'days', 'inst1_1', 'inst1_2', 'inst2_1', 'inst2_2',
                                          'inst3_1', 'inst3_2', 'inst4_1', 'inst4_2', 'inst5_1', 'inst5_2')) + '"'

        for type, days in types.iteritems():

            p1, p2 = type.split('###')
            days = '-'.join(map(str, days))
            sample_instances = random.sample(instances_by_type[type], 5)

            sample_instances = [(sf_p1.replace('{a0}', "<font color='#d95f02'>%s</font>" % s1_a0).
                                 replace('{a1}', "<font color='#7570b3'>%s</font>" % s1_a1),
                                 sf_p2.replace('{a0}', "<font color='#d95f02'>%s</font>" % s2_a0).
                                 replace('{a1}', "<font color='#7570b3'>%s</font>" % s2_a1))
                                for (sf_p1, s1_a0, s1_a1, sf_p2, s2_a0, s2_a1) in sample_instances]

            sample_instances = [item for lst in sample_instances for item in lst]

            print >> f_out, '"' + '","'.join([p1.replace('"', "''"), p2.replace('"', "''"), days] + sample_instances) + '"'


if __name__ == '__main__':
    main()
