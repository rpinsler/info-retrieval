import lda

import os
import pickle

import numpy as np
from numpy.linalg import norm

from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords

STOP_WORDS = stopwords.words('english')
TEMP_DIR = "./temp"


class SimilarVenueYear():
    def __init__(self):
        self.vocab = []
        self.venue_year_names = []
        self.model = None

    def lda_modeling(self, context, n_topics=10, n_iter=100, min_df=10):
        venue_year_titles = {}
        for cnt, (event, elem) in enumerate(context):
            title = elem.find('title')
            venue = None
            if elem.tag == 'article':
                venue = elem.find('journal')
            elif elem.tag == 'inproceedings':
                venue = elem.find('booktitle')
            year = elem.find('year')
            if title is not None and venue is not None and year is not None and title.text is not None:
                title = title.text.lower()
                venue = venue.text
                year = year.text
                if venue + year not in venue_year_titles:
                    venue_year_titles[venue + year] = ''
                venue_year_titles[venue + year] += '' + title
            elem.clear()
            # Also eliminate now-empty references from the root node to elem
            for ancestor in elem.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        del context

        cv = CountVectorizer(stop_words='english', min_df=min_df)
        self.venue_year_names = venue_year_titles.keys()

        features = cv.fit_transform(venue_year_titles.values()).toarray()
        self.vocab = zip(*sorted(cv.vocabulary_.iteritems(), key=lambda k: k[1]))[0]
        self.model = lda.LDA(n_topics=n_topics, random_state=0, n_iter=n_iter)
        self.model.fit(features)

        self.write_to_file()

    def print_topic_words(self, n_topics='all', n_top_words=8):
        topic_word = self.model.topic_word_
        if not n_topics == 'all':
            topic_word = topic_word[:n_topics]
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(self.vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
            print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    def query_venue_year(self, venue, year, top_k):
        query_venue_year_name = venue + year
        query_id = self.venue_year_names.index(query_venue_year_name)
        doc_topic = self.model.doc_topic_
        all_sim = []
        for i in xrange(doc_topic.shape[0]):
            sim = doc_topic[i].dot(doc_topic[query_id]) / norm(doc_topic[i]) / norm(doc_topic[query_id])
            all_sim.append(sim)
        print "Query:", venue, year
        print
        sorted_item = sorted(range(len(all_sim)), key=lambda k: all_sim[k], reverse=True)
        sorted_sim = sorted(all_sim, key=lambda k: k, reverse=True)
        for i in xrange(1, top_k + 1):
            venue_year = self.venue_year_names[sorted_item[i]]
            venue = venue_year[:-4]
            year = venue_year[-4:]
            print venue, year, sorted_sim[i]
        print

    def write_to_file(self):
        if not os.path.isdir(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        pickle.dump(self.model, open(TEMP_DIR + '/lda_model.obj', 'w'))
        pickle.dump(self.venue_year_names, open(TEMP_DIR + '/venue_year_names.obj', 'w'))
        pickle.dump(self.vocab, open(TEMP_DIR + '/vocab.obj', 'w'))

    def load_from_file(self):
        self.model = pickle.load(open(TEMP_DIR + '/lda_model.obj', 'r'))
        self.venue_year_names = pickle.load(open(TEMP_DIR + '/venue_year_names.obj', 'r'))
        self.vocab = pickle.load(open(TEMP_DIR + '/vocab.obj', 'r'))