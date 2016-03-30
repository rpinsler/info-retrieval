import os
import lucene
import json
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from lxml import etree
from search import Searcher
from index import Indexer, CustomAnalyzer
from utils import check_config

INDEX_DIR = 'index'
DATA_DIR = 'data/dblp.xml'
# DATA_DIR = 'data/dblp_small.xml'

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)
    config = check_config(config)
    lucene.initVM()

    # index documents
    title_analyzer = CustomAnalyzer(config['titleAnalyzer'])
    per_field = HashMap()
    per_field.put("title", title_analyzer)
    analyzer = PerFieldAnalyzerWrapper(
                StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
    Indexer(DATA_DIR, INDEX_DIR, analyzer)
    # searcher = Searcher(INDEX_DIR, analyzer)
    # q = raw_input("Query: ")
    # searcher.search(q, N = config['topN'])
    #searcher.run(config['topN'])
