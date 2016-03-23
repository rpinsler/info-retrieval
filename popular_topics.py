import os
from collections import Counter

import nltk
from nltk import word_tokenize
from nltk.tag.perceptron import PerceptronTagger

import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from search import Searcher
from index import CustomAnalyzer


class PopularTopics:
    def __init__(self, index_dir, analyzer):
        self.searcher = Searcher(index_dir, analyzer)

    def dict_append(self, entity, f_dist):
        entity = ' '.join(entity)
        if entity not in f_dist:
            f_dist[entity] = 0
        f_dist[entity] += 1

    def get_popular_topics(self, q_year, top_k):
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

        unigram_result = Counter(unigram_dist).most_common(int(len(unigram_dist) * 0.01) + top_k)[int(len(unigram_dist) * 0.01):]
        bigram_result = Counter(bigram_dist).most_common(top_k)
        trigram_result = Counter(trigram_dist).most_common(top_k)

        result = unigram_result + bigram_result + trigram_result
        result = sorted(result, key=lambda k: k[1], reverse=True)[:top_k]
        return result