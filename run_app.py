import sys
import lucene
import json
from lxml import etree
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from index import Indexer, CustomAnalyzer
from utils import check_config


CONFIG_DIR = 'config.json'
INDEX_DIR = 'index'
DATA_DIR = 'data/dblp.xml'
TAGS = ('article', 'inproceedings')


def run_app1(top_k):
    from popular_topics import PopularTopics

    pt = PopularTopics(INDEX_DIR, analyzer)
    while 1:
        query_year = raw_input("Query for a year: ")
        results = pt.get_popular_topics(query_year, top_k=top_k)  # top_k is set to 10.
        print results
        if query_year == '':
            sys.exit(0)


def run_app2(n_topics, n_iter, top_k):
    from similar_venue_year import SimilarVenueYear
    svy = SimilarVenueYear()
    svy.lda_modeling(context, n_topics=n_topics, n_iter=n_iter)
    while 1:
        query_venue, query_year = raw_input("Query for a venue and year: ").split()
        results = svy.query_venue_year(venue=query_venue, year=query_year, top_k=top_k)  # top_k is set to 10.
        print results
        if query_year == '':
            sys.exit(0)


if __name__ == '__main__':
    with open(CONFIG_DIR) as f:
            config = json.load(f, encoding='ascii')
            config = check_config(config)

    lucene.initVM()  # start JVM for Lucene

    title_analyzer = CustomAnalyzer(config['titleAnalyzer'])
    per_field = HashMap()
    per_field.put("title", title_analyzer)
    analyzer = PerFieldAnalyzerWrapper(
                StandardAnalyzer(Version.LUCENE_CURRENT), per_field)

    context = etree.iterparse(DATA_DIR, events=('end',),
                                  tag=TAGS,
                                  dtd_validation=True)

    run_app1(top_k=10)
    run_app2(n_topics=10, n_iter=100, top_k=10)
