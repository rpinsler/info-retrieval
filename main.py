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
    base_dir = os.path.expanduser("~") + "/Semester_NTU/" + \
               "10 Information Retrieval and Analysis/info-retrieval"
    topN = 10

    lucene.initVM()

    # create XML document context
    context = etree.iterparse(DATA_DIR, events=('end',),
                              tag=('article', 'inproceedings'),
                              dtd_validation=True)
    # index documents
    config = {'lowercase': False, 'stemming': True, 'stopwords': True}
    title_analyzer = CustomAnalyzer(config)
    per_field = HashMap()
    per_field.put("title", title_analyzer)
    analyzer = PerFieldAnalyzerWrapper(
                StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
    Indexer(os.path.join(base_dir, INDEX_DIR), context, analyzer)

    print('Finished indexing.')
    searcher = Searcher(os.path.join(base_dir, INDEX_DIR), analyzer)
    # q = raw_input("Query: ")
    # searcher.search(q, topN)
    searcher.run(topN)
