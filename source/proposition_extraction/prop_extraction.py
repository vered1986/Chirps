"""
author: Gabi Stanovsky

Usage:
    prop_extraction --in=INPUT_FILE --out=OUTPUT_FILE

Extract propositions from a given input file, output is produced in separate output file.
If both in and out paramaters are directories, the script will iterate over all *.txt files in the input directory and
output to *.prop files in output directory.

Options:
   --in=INPUT_FILE    The input file, each sentence in a separate line
   --out=OUTPUT_FILE  The output file, Each extraction in a tab separated line, each consisting of original sentence,
   predicate template, lemmatized predicate template,argument name, argument value, ...
"""
import os
import sys
import ntpath
import codecs
import logging

sys.path.append('../')

from glob import glob
from docopt import docopt
from spacy_wrapper import spacy_wrapper


logging.basicConfig(level = logging.INFO)


def main():

    args = docopt(__doc__)
    inp = args['--in']
    out = args['--out']
    logging.info("Loading spaCy...")
    pe = prop_extraction()

    # Differentiate between single input file and directories
    if os.path.isdir(inp):
        logging.debug('Running on directories:')
        num_of_lines = num_of_extractions = 0

        for input_fn in glob(os.path.join(inp, '*.txt')):
            output_fn = os.path.join(out, path_leaf(input_fn).replace('.txt', '.prop'))
            logging.debug('input file: {}\noutput file:{}'.format(input_fn, output_fn))

            cur_line_counter, cur_extractions_counter = run_single_file(input_fn, output_fn, pe)
            num_of_lines += cur_line_counter
            num_of_extractions += cur_extractions_counter

    else:
        logging.debug('Running on single files:')
        num_of_lines, num_of_extractions = run_single_file(inp, out, pe)

    logging.info('# Sentences: {} \t #Extractions: {} \t Extractions/sentence Ratio: {}'.
                 format(num_of_lines, num_of_extractions, float(num_of_extractions) / num_of_lines))


class prop_extraction:
    """
    Lenient proposition extraction -- assumes all modifications are non-restrictive
    """
    def __init__(self):
        """
        Initalize internal parser
        """
        self.parser = spacy_wrapper()

    def get_extractions(self, sent):
        """
        Given a sentence, get all of its propositions.
        :param sent: the sentence
        :return A list of strings, each representing a single proposition.
        """
        ret = []

        try:
            self.parser.parse(sent)
            self.parser.chunk()

            for verb in [i for i in range(self.parser.get_len()) if self.parser.is_verb(i)]:

                # Extract the proposition from this predicate
                extraction = Extraction()

                # For each child, decide if and how to include it in the template
                for child in self.parser.get_children(verb):

                    curr_arg = child

                    # Find if this is the right spot to plug the verb in the template
                    if curr_arg > verb and not extraction.pred_exists:
                        extraction.set_predicate(self.parser.get_text(verb), self.parser.get_lemma(verb))

                    # Add non-consecutive particles to predicate
                    if self.parser.is_part_of_non_consecutive_span(verb, curr_arg):
                        extraction.add_prt_to_predicate(self.parser.get_text(curr_arg),
                                                        self.parser.get_lemma(curr_arg))

                    # Datives and prepositions are deferred if they have one exactly one pobj
                    if self.parser.is_dative(curr_arg) or self.parser.is_prep(curr_arg):

                        pobjs = self.parser.get_single_pobj(curr_arg)

                        if pobjs:

                            # Sanity check
                            assert(len(pobjs)) == 1
                            pobj = pobjs[0]

                            # Plug prep/dative in template and signal that pobj should be added to roles_dict
                            # note - we do not lemmatize the datives and pp's
                            extraction.template += "{} ".format(self.parser.get_text(curr_arg))
                            curr_arg = pobj

                    # Subject and objects are plugged directly
                    if self.parser.is_subj(curr_arg):

                        # Replace pronoun with head of a relative clause
                        if self.parser.is_rel_clause(verb) and self.parser.is_pronoun(curr_arg):
                            extraction.add_argument(self.parser.get_text(self.parser.get_head(verb)))
                        else:
                            extraction.add_argument(self.parser.get_text(curr_arg))

                    if self.parser.is_obj(curr_arg):
                        extraction.add_argument(self.parser.get_text(curr_arg))

                # Record extractions with at least 2 arguments
                if len(extraction.args) > 1 and extraction.pred_exists:
                    ret.append(str(extraction))

        except:
            pass

        return ret


class Extraction:
    """
    A representation of an extraction, composed of a single predicate and an arbitrary (>0) number of arguments.
    """
    def __init__(self):
        self.args = []
        self.roles_dict = {}
        self.template = ''
        self.pred_exists = False

    def set_predicate(self, pred_text, lemmatized_pred_text):
        """
        Add the predicate and its lemmatized version to this template
        :param pred_text: the predicate template
        """
        self.template += '{} '.format(pred_text)
        self.pred = pred_text
        self.lemmatized_pred = lemmatized_pred_text
        if self.pred != self.lemmatized_pred:
            logging.debug('Lemmatized: {} / {}'.format(self.pred, self.lemmatized_pred))
        self.pred_exists = True

    def add_prt_to_predicate(self, prt_text, lemmatized_prt_text):
        """
        Adds a particle to the predicate
        :param prt_text: the particle text
        :param lemmatized_prt_text: the lemmatized particle text
        """
        self.template += '{} '.format(prt_text)
        self.pred += ' ' + prt_text
        self.lemmatized_pred += ' ' + lemmatized_prt_text
        logging.debug('Added particle: {}'.format(prt_text))

    def add_argument(self, arg_text):
        """
        Add a new argument to the extraction
        Adds to template and roles_dict, by assuming the next index after the last argument.
        :param arg_text: the argument text
        """
        arg_index = len(self.args)
        self.args.append(arg_text)
        self.roles_dict[arg_index] = arg_text  # Note: This ignores all internal modifications
        self.template += '{A' + str(arg_index) + '} '

    def __str__(self):
        """
        Textual representation of this extraction for an output file.
        """
        self.template = self.template.lstrip().rstrip()
        # create a lemmatized template, by replacing the predicate slot with its lemma
        self.lemmatized_template = self.template.replace(self.pred, self.lemmatized_pred)
        ret = '\t'.join([self.template, self.lemmatized_template] +
                        ['A{}\t{}'.format(key, val)
                         for key, val in sorted(self.roles_dict.iteritems(), key = lambda (k,_): k)])
        return ret


def run_single_file(input_fn, output_fn, prop_ex):
    """
    Process extractions from a single input file and print to an output file,
    using a proposition extraction module.
    :param input_fn: the input file name
    :param output_fn: the output file name
    :param prop_ex: the proposition extraction object
    :return (#lines, #num of extractions)
    """
    logging.info('Reading sentences from {}'.format(input_fn))
    ex_counter = 0
    line_counter = 0

    with codecs.open(output_fn, 'w', 'utf-8') as f_out:
        for line in open(input_fn):
            line_counter += 1
            data = line.strip().split('\t')
            tweet_id = None
            if len(data) == 2:
                tweet_id, sent = data
            elif len(data) == 4:
                date, tweet_id, user, sent = data
            else:
                # Not at tweet, just fill in the id with a place holder
                tweet_id = 'NONE'
                sent = data[0]
            logging.info('Read: {}'.format(sent))
            for ex in prop_ex.get_extractions(sent):
                to_print = '\t'.join(map(str, [tweet_id, sent, ex])).decode('ascii', errors = 'ignore')
                logging.debug(to_print)
                f_out.write(to_print + "\n")
                ex_counter += 1

    logging.info('Done! Wrote {} extractions to {}'.format(ex_counter, output_fn))
    return line_counter, ex_counter


def path_leaf(path):
    """
    Get just the filename from the full path.
    http://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

if __name__ == '__main__':
    main()

