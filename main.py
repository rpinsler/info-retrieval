import os
import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from lxml import etree
from search import Searcher
from index import Indexer, CustomAnalyzer

INDEX_DIR = 'index'
# DATA_DIR = 'data/dblp.xml'
DATA_DIR = 'data/dblp_small.xml'

if __name__ == "__main__":
    # user inputs
    topN = 10

    lucene.initVM()

    # index documents
    config = {'lowercase': True, 'stemming': True, 'stopwords': True}
    title_analyzer = CustomAnalyzer(config)
    per_field = HashMap()
    per_field.put("title", title_analyzer)
    analyzer = PerFieldAnalyzerWrapper(
                StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
    # Indexer(DATA_DIR, INDEX_DIR, analyzer)
    searcher = Searcher(INDEX_DIR, analyzer)
    q = raw_input("Query: ")
    searcher.search(q)
    #searcher.run(topN)
