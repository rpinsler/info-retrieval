import lucene
import json
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from index import Indexer, CustomAnalyzer
from utils import check_config

CONFIG_DIR = 'config.json'
INDEX_DIR = 'index'
DATA_DIR = 'data/dblp.xml'

# build index from provided dataset
if __name__ == "__main__":
    with open(CONFIG_DIR) as f:
        config = json.load(f, encoding='ascii')
        config = check_config(config)

    lucene.initVM()  # start JVM for Lucene

    # index documents
    # use different analyzer for title field
    title_analyzer = CustomAnalyzer(config['titleAnalyzer'])
    per_field = HashMap()
    per_field.put("title", title_analyzer)
    analyzer = PerFieldAnalyzerWrapper(
                StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
    Indexer(DATA_DIR, INDEX_DIR, analyzer)
