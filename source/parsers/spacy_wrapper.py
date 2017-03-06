"""
author: Gabi Stanovsky
Abstraction over the spaCy parser, all output uses word indexes. Also offers VP and NP chunking as spaCy primitives.
"""

import logging

from spacy.en import English
from spacy.tokens import Span
from collections import defaultdict

logging.basicConfig(level = logging.DEBUG)


class spacy_wrapper:
    """
    Abstraction over the spaCy parser, all output uses word indexes. Also offers VP and NP chunking as spaCy primitives.
    """
    def __init__(self):

        self.nlp = English(ner = False)

        # workaround for non-consecutive spans, these cannot be merged to single native spacy spans,
        # store them here instead - this is supported only for VP chunk
        self.reset()
        self.idx_to_word_index = {}

    def parse(self, sent):
        """
        Parse a raw sentence - shouldn't return a value, but properly change the internal status
        :param sent - a raw sentence
        """
        self.reset()
        self.toks = self.nlp(unicode(sent, errors = 'ignore'))
        self.idx_to_word_index = self.get_idx_to_word_index()

    def reset(self):
        """
        Reset the internal state of the parser, should be called internally prior to parse
        """
        self.non_consecutive_spans = defaultdict(lambda: [])

    def get_sents(self):
        """
        Returns a list of sentences
        :return: a list of sentences
        """
        return [s for s in self.parser.sents]
	
    def chunk(self):
        """
        Run all chunking on the current sentence
        """
        self.np_chunk()
        self.vp_chunk()
        self.pp_chunk()

    def np_chunk(self):
        """
        spaCy noun chunking, will appear as single token
        See: https://github.com/explosion/spaCy/issues/156
        """
        for np in self.toks.noun_chunks:
            np.merge(np.root.tag_, np.text, np.root.ent_type_)

        # Update mappings
        self.idx_to_word_index = self.get_idx_to_word_index()

    def vp_chunk(self):
        """
        Verb phrase chunking - head is a verb and children are auxiliaries
        """
        self.chunk_by_filters(head_filter = lambda head: self.is_verb(head),
                              child_filter =lambda child: \
                              (self.is_aux(child) and len(self.get_children(child)) == 0) \
                              or (self.is_neg(child) and len(self.get_children(child)) == 0)\
                              or (self.is_prt(child) and len(self.get_children(child)) == 0))

    def pp_chunk(self):
        """
        PP phrase chunking - head is a PP with a single PP child
        """
        def pp_head_filter(head):
            if not self.is_prep(head):
                return False
            children = self.get_children(head)
            if len(children) != 1:
                return False
            return self.is_prep(children[0])

        self.chunk_by_filters(head_filter = pp_head_filter, child_filter = lambda child: self.is_prep(child))

    def is_part_of_non_consecutive_span(self, head, tok):
        """
        Returns True iff tok is part of a non-consecutive span headed by head
        :param head: the head
        :param tok: a token
        :return: whether tok is part of a non-consecutive span headed by head
        """
        return (head in self.non_consecutive_spans) and (tok in self.non_consecutive_spans[head])

    def chunk_by_filters(self, head_filter, child_filter):
        """
        Meta chunking function, given head and children filters, collapses them together.
        Both head_filter and child_filter are functions taking a single argument - the node index.
        :param head_filter: head filter
        :param child_filter: child filter
        """

        # Collect verb chunks - dictionary from verb index to chunk's word indices '''
        chunks = defaultdict(lambda: [])
        for head in [i for i, _ in enumerate(self.toks) if head_filter(i)]:
            for child in [child for child in self.get_children(head) if child_filter(child)]:
                chunks[head].append(child)

        # Create Spans
        consecutive_chunks = {}
        for head, span in chunks.iteritems():

            # The head itself is always part of a non-empty span
            span.append(head)
            span = sorted(span)

            # For non-consecutive spans - store in the class member, these will be dealt with externally.
            # Remove head from non-consecutive span to ease this external handling
            if not consecutive(span):
                self.non_consecutive_spans[head] = [tok for tok in span if tok != head]

            # Calculate and store the span's lemma
            else:
                span_lemma = ' '.join([self.get_lemma(tok) for tok in span])
                consecutive_chunks[head] = (Span(self.toks, span[0], span[-1] + 1), span_lemma)

        # Merge consecutive spans to chunks, this is done after creating all Span objects to avoid index changing while iterating
        for head, (chunk, chunkLemma) in consecutive_chunks.iteritems():

            # Set the span's lemma
            chunk.merge(chunk.root.tag_, chunkLemma, chunk.root.ent_type_) # tag, lemma, ent_type

        # Update mappings
        self.idx_to_word_index = self.get_idx_to_word_index()

    def get_idx_to_word_index(self):
        """
        Create a mapping from idx to word index
        :return: a mapping from idx to word index
        """
        return dict([(tok.idx, i) for (i, tok) in enumerate(self.toks)])

    def get_pos(self, ind):
        """
        Return the pos of token at index ind
        :param ind: the index
        :return: the pos of token at index ind
        """
        return self.toks[ind].tag_

    def get_rel(self, ind):
        """
        Return the dependency relation of token at index ind
        :param ind: the index
        :return: the dependency relation of token at index ind
        """
        return self.toks[ind].dep_

    def get_word(self, ind):
        """
        Return the surface form of token at index ind
        :param ind: the index
        :return: the surface form of token at index ind
        """
        return self.toks[ind].orth_

    def get_lemma(self, ind):
        """
        Return the surface form of token at index ind
        :param ind: the index
        :return: the surface form of token at index ind
        """
        return self.toks[ind].lemma_

    def get_head(self, ind):
        """
        Return the word index of the head of of token at index ind
        :param ind: the index
        :return: the word index of the head of of token at index ind
        """
        return self.idx_to_word_index[self.toks[ind].head.idx]

    def get_children(self, ind):
        """
        Return a sorted list of children of a token
        :param ind: the index
        :return: a sorted list of children of a token
        """

        # TODO: do we have to use sorted here? Maybe spaCy already returns a sorted list of children
        return sorted([self.idx_to_word_index[child.idx] for child in self.toks[ind].children])

    def get_char_start(self, ind):
        """
        Get the start character index of this word
        :param ind: the index
        :return: the start character index of this word
        """
        return self.toks[ind].idx

    def get_char_end(self, ind):
        """
        Get the end character index of this word
        :param ind: the index
        :return: the end character index of this word
        """
        return self.toks[ind].idx + len(self.get_word(ind))

    def is_root(self, ind):
        """
        Returns True iff the token at index ind is the head of this tree
        :param ind: the index
        :return: True iff the token at index ind is the head of this tree
        """
        return (self.toks[ind].head is self.toks[ind])

    def get_len(self):
        """
        Returns the number of tokens in the current sentence
        :return: the number of tokens in the current sentence
        """
        return len(self.toks)

    def is_verb(self, ind):
        """
        Returns whether this token is a verb
        :param ind: the index
        :return: Is this token a verb
        """
        return self.get_pos(ind).startswith('VB')

    def is_pronoun(self, ind):
        """
        Returns whether this token is a pronoun
        :param ind: the index
        :return: Is this token a pronoun
        """
        return self.get_pos(ind).startswith('WP')

    def is_aux(self, ind):
        """
        Returns whether this token is an auxiliary
        :param ind: the index
        :return: Is this token a auxiliary
        """
        return self.get_rel(ind).startswith('aux')

    def is_neg(self, ind):
        """
        Returns whether this token is a negation
        :param ind: the index
        :return: Is this token a negation
        """
        return self.get_rel(ind).startswith('neg')

    def is_prt(self, ind):
        """
        Returns whether this token is a particle
        :param ind: the index
        :return: Is this token a particle
        """
        return self.get_rel(ind).startswith('prt')

    def is_dative(self, ind):
        """
        Returns whether this token is a dative
        :param ind: the index
        :return: Is this token a dative
        """
        return self.get_rel(ind).startswith('dative')

    def is_prep(self, ind):
        """
        Returns whether this token is a preposition
        :param ind: the index
        :return: Is this token a preposition
        """
        return self.get_rel(ind).startswith('prep')

    def is_subj(self, ind):
        """
        Returns whether this token is a subject
        :param ind: the index
        :return: Is this token a subject
        """
        return 'subj' in self.get_rel(ind)

    def is_obj(self, ind):
        """
        Returns whether this token is an object
        :param ind: the index
        :return: Is this token a object
        """
        rel = self.get_rel(ind)
        return ('obj' in rel) or ('attr' in rel)

    def is_rel_clause(self, ind):
        """
        Returns whether this token is a relative clause
        :param ind: the index
        :return: Is this token a relative clause
        """
        return 'relcl' in self.get_rel(ind)

    def get_single_pobj(self, ind):
        """
        Get Pobj, only if there's exactly one such child
        :param ind: the index
        :return: Pobj, only if there's exactly one such child
        """
        pobjs = [child for child in self.get_children(ind) if self.get_rel(child) == 'pobj']
        if len(pobjs) == 1:
            return pobjs

        # TODO: what to do if there's zero or more than one pobj?
        return []

    def get_text(self, ind):
        """
        Get the text of this node
        :param ind: the index
        :return: the text of this node
        """
        return self.toks[ind].text

        
def consecutive(span):
    """
    Check if a span of indices is consecutive
    :param span: the span of indices
    :return: whether the span of indices is consecutive
    """
    return [i - span[0] for i in span] == range(span[-1] - span[0] + 1)
