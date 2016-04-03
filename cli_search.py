import lucene
import json
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from search import Searcher
from index import CustomAnalyzer
from utils import check_config

CONFIG_DIR = 'config.json'
INDEX_DIR = 'index'
DATA_DIR = 'data/dblp.xml'

# run search on command line
# see ui_search.py to use the search via web UI
if __name__ == "__main__":
    with open(CONFIG_DIR) as f:
        config = json.load(f)
    config = check_config(config)

    lucene.initVM()  # start JVM for Lucene

    # index documents
    # use different analyzer for title field
    title_analyzer = CustomAnalyzer(config['titleAnalyzer'])
    per_field = HashMap()
    per_field.put("title", title_analyzer)
    analyzer = PerFieldAnalyzerWrapper(
                StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
    searcher = Searcher(INDEX_DIR, analyzer)
    # q = raw_input("Query: ")
    # searcher.search(q, N=config['topN'])
    searcher.run(config['topN'])
