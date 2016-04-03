from collections import Counter

import nltk
from nltk import word_tokenize
from nltk.tag.perceptron import PerceptronTagger

from search import Searcher


class PopularTopics:
    """
    Retrieves popular research topics for given year.
    """

    def __init__(self, index_dir, analyzer):
        """
        Initializes searcher.
        """
        self.searcher = Searcher(index_dir, analyzer)

    def dict_append(self, entity, f_dist):
        """
        Adds entity to dictionary.
        """
        entity = ' '.join(entity)
        if entity not in f_dist:
            f_dist[entity] = 0
        f_dist[entity] += 1

    def get_popular_topics(self, q_year, top_k):
        """
        Retrieves popular research topics for given year.
        """
        titles = self.searcher.search_year(q_year)
        unigram_dist = {}
        bigram_dist = {}
        trigram_dist = {}
        ngram_dist = {}

        tagset = None
        tagger = PerceptronTagger()
        grammar = "NP: {<JJ>*(<NN>|<NNS>)*<NN>(<NN>|<NNS>)*}"
        cp = nltk.RegexpParser(grammar)
        for title in titles:
            title = title.lower()
            text = word_tokenize(title)
            sentence = nltk.tag._pos_tag(text, tagset, tagger)
            result = cp.parse(sentence)

            # retrieve uni-, bi- and trigrams from result set
            for node in list(result):
                if isinstance(node, nltk.tree.Tree):
                    entity = zip(*list(node))[0]
                    if len(entity) == 1:
                        self.dict_append(entity, unigram_dist)
                    elif len(entity) == 2:
                        self.dict_append(entity, bigram_dist)
                    elif len(entity) == 3:
                        self.dict_append(entity, trigram_dist)
                    else:
                        self.dict_append(entity, ngram_dist)

        top1p = int(len(unigram_dist) * 0.01)
        unigram_result = Counter(unigram_dist).most_common(top1p + top_k)[top1p:]
        bigram_result = Counter(bigram_dist).most_common(top_k)
        trigram_result = Counter(trigram_dist).most_common(top_k)

        result = unigram_result + bigram_result + trigram_result
        result = sorted(result, key=lambda k: k[1], reverse=True)[:top_k]
        return result
