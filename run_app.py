import lucene
import json
from lxml import etree
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from index import CustomAnalyzer
from utils import check_config


CONFIG_DIR = 'config.json'
INDEX_DIR = 'index'
DATA_DIR = 'data/dblp.xml'
TAGS = ('article', 'inproceedings')


def run_app1(top_k):
    from popular_topics import PopularTopics
    pt = PopularTopics(INDEX_DIR, analyzer)
    while True:
        print
        print("Search for most popular topics in a given year. Press enter with no input to continue.")
        query_year = raw_input("Year: ")
        if query_year == '':
            return

        results = pt.get_popular_topics(query_year, top_k=top_k)
        print
        print("Results:")
        for i, res in enumerate(results):
            print("%d) %s (%s)") % (i+1, res[0], res[1])


def run_app2(n_topics, n_iter, top_k):
    from similar_venue_year import SimilarVenueYear
    svy = SimilarVenueYear()
    context = etree.iterparse(DATA_DIR, events=('end',),
                              tag=TAGS, dtd_validation=True)
    print
    print("Search for most similar publication venues and years. This requires to first run LDA (may take some minutes).")
    cont = raw_input("Do you want to continue? (y/n): ")
    if cont == 'n':
        return
    elif cont != 'y':
        print "Invalid input. Stopping here."
        return

    print("Running LDA...")
    svy.lda_modeling(context, n_topics=n_topics, n_iter=n_iter)
    print("Finished LDA.")
    while True:
        print
        print("Search for most similar publication venues and years. Press enter with no input to continue.")
        query_venue = raw_input("Venue: ")
        if query_venue == '':
            return
        query_year = raw_input("Year: ")
        results = svy.query_venue_year(venue=query_venue, year=query_year, top_k=top_k)
        if results is not None:
            print
            print("Results:")
            for i, res in enumerate(results):
                print("%d) %s (%.4f)") % (i+1, res[0] + " " + str(res[1]), res[2])


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

    run_app1(top_k=10)
    run_app2(n_topics=10, n_iter=100, top_k=10)
