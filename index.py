from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer, \
     StandardTokenizer, StandardFilter
from org.apache.lucene.document import Document, StringField, TextField, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.pylucene.analysis import PythonAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import LowerCaseFilter, StopFilter, \
     StopAnalyzer, SimpleAnalyzer, WhitespaceAnalyzer
from org.apache.lucene.analysis.en import PorterStemFilter

from lxml import etree
import os


class CustomAnalyzer(PythonAnalyzer):
    def __init__(self, config):
        self.lowercase = config['lowercase']
        self.stemming = config['stemming']
        self.stopwords = config['stopwords']
        PythonAnalyzer.__init__(self)

    def createComponents(self, fieldName, reader):
        source = StandardTokenizer(Version.LUCENE_CURRENT, reader)
        tfilter = StandardFilter(Version.LUCENE_CURRENT, source)
        if self.lowercase:
            tfilter = LowerCaseFilter(Version.LUCENE_CURRENT, tfilter)
        if self.stemming:
            tfilter = PorterStemFilter(tfilter)
        if self.stopwords:
            tfilter = StopFilter(Version.LUCENE_CURRENT, tfilter,
                                 StopAnalyzer.ENGLISH_STOP_WORDS_SET)
        return self.TokenStreamComponents(source, tfilter)


class Indexer():
    def __init__(self, store_dir, context, analyzer):

        if not os.path.exists(store_dir):
            os.mkdir(store_dir)

        store = SimpleFSDirectory(File(store_dir))
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        self.writer = IndexWriter(store, config)
        self.index(context)
        self.complete_index()

    def index(self, context):
        """
        http://lxml.de/parsing.html#modifying-the-tree
        Based on Liza Daly's fast_iter
        http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        See also http://effbot.org/zone/element-iterparse.htm
        """
        for event, elem in context:
            self.index_document(elem)
            # It's safe to call clear() here because no descendants will be
            # accessed
            elem.clear()
            # Also eliminate now-empty references from the root node to elem
            for ancestor in elem.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        del context

    def index_document(self, elem):

        # meaning of Field.Store.YES:
        # Store the original field value in the index.
        # This is useful for short texts like a document's title which should
        # be displayed with the results. The value is stored in its
        # original form, i.e. no analyzer is used before it is stored.

        try:
            doc = Document()
            # remove <i></i> tags etc. that are sometimes used
            etree.strip_tags(elem, 'i', 'ref', 'sub', 'sup', 'tt')
            # index but don't tokenize id
            doc.add(StringField('id', elem.get('key'), Field.Store.YES))
            for ch in elem:
                if ch.tag == 'title':
                    doc.add(TextField('title', ch.text, Field.Store.YES))
                elif ch.tag == 'author':
                    doc.add(TextField('authors', ch.text, Field.Store.YES))
                elif ch.tag == 'year':
                    # IntField allows range searches, but it's more difficult
                    # doc.add(IntField('year', int(ch.text), Field.Store.YES))
                    doc.add(StringField('year', ch.text, Field.Store.YES))
                elif ch.tag == 'journal' or ch.tag == 'booktitle':
                    doc.add(TextField('venue', ch.text, Field.Store.YES))

            self.writer.addDocument(doc)
        except Exception, e:
            print "Indexing error:", e

    def complete_index(self):
        # self.writer.optimize()
        self.writer.close()
