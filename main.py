import lucene
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from java.io import File

from lxml import etree
from search import search
from index import Indexer

if __name__ == "__main__":
    # DATA_DIR = 'data/dblp.xml'
    DATA_DIR = 'data/dblp_small.xml'
    INDEX_DIR = 'index'
    topN = 100

    lucene.initVM()

    # create XML document context
    context = etree.iterparse(DATA_DIR, events=('end',),
                              tag=('article', 'inproceedings'),
                              dtd_validation=True)
    # index documents
    Indexer(INDEX_DIR, context)

    q = raw_input("Query:")
    directory = SimpleFSDirectory(File(INDEX_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    # analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    search(q, searcher, analyzer, topN)
