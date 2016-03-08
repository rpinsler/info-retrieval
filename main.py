import os
import lucene
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap
from java.io import File

from lxml import etree
from search import search
from index import Indexer, CustomAnalyzer

INDEX_DIR = 'index'
# DATA_DIR = 'data/dblp.xml'
DATA_DIR = 'data/dblp_small.xml'

if __name__ == "__main__":

    # user inputs
    base_dir = os.path.expanduser("~") + \
               "/Semester_NTU/10 Information Retrieval and Analysis/info-retrieval"
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

    print('Finished indexing. You can search now,' +
          ' but currently only on the title field.' +
          ' Try e.g. "optimization".')
    q = raw_input("Query: ")
    directory = SimpleFSDirectory(File(INDEX_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    # analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    search(q, searcher, analyzer, topN)
