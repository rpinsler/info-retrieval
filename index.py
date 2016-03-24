from java.io import File
from java.util import HashSet, Arrays
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
import random
import HTMLParser

TAGS = ('article', 'inproceedings')
HTML_TAGS = ('i','ref','sub','sup','tt')
FIELDS = ['title', 'author', 'year', 'journal', 'booktitle']
DUMP_RANDOM_DOCS = False


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
            # EnglishMinimalStemFilter, KStemFilter and PorterStemFilter
            tfilter = PorterStemFilter(tfilter)
        if self.stopwords:
            # words = [line.rstrip('\n') for line
            #          in open('stopwords/english_default.txt')]
            words = StopAnalyzer.ENGLISH_STOP_WORDS_SET
            # HashSet(Arrays.asList(words))
            tfilter = StopFilter(Version.LUCENE_CURRENT, tfilter, words)
        return self.TokenStreamComponents(source, tfilter)


class Indexer():
    def __init__(self, data_dir, store_dir, analyzer, verbose=True):

        if not os.path.exists(store_dir):
            os.mkdir(store_dir)

        store = SimpleFSDirectory(File(store_dir))
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        self.writer = IndexWriter(store, config)
        self.htmlparser = HTMLParser.HTMLParser()
        self.ndocs = 0
        self.verbose = verbose
        if DUMP_RANDOM_DOCS:
            N = 856
            k = 100
            random.seed(0)
            self.randdocs = sorted(random.sample(range(1, N+1), k=k))
        self.index(data_dir)
        self.complete_index()

        if self.verbose:
            print "Finished indexing. %d documents indexed in total." % self.ndocs

    def extract_document(self, doc, index):
        with open("eval/qrels_manual/random_doc_selection", "a") as f:
            f.write('%d) ' % (index+1))
            key = doc['id'].encode("utf-8")
            title = doc['title'].encode("utf-8")
            authors = ''
            for author in doc.getValues('authors'):
                authors += author.encode("utf-8") + ', '
            authors = authors[:-2]
            year = doc['year'].encode("utf-8")
            venue = doc['venue'].encode("utf-8")
            f.write('%s\n title: %s\n authors: %s\n year: %s\n venue: %s\n'
                    % (key, title, authors, year, venue))

            with open("eval/qrels_manual/qrels", "a") as f:
                f.write('TOPIC_NUM\t0\t%s\t \n' % doc['id'])

    def index(self, data_dir):
        """
        http://lxml.de/parsing.html#modifying-the-tree
        Based on Liza Daly's fast_iter
        http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        See also http://effbot.org/zone/element-iterparse.htm
        """

        context = etree.iterparse(data_dir, events=('end',),
                                  tag=TAGS,
                                  dtd_validation=True)

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
        try:
            doc = Document()
            # remove <i></i> tags etc. that are sometimes used
            etree.strip_tags(elem, HTML_TAGS)
            doc.add(StringField('id', elem.get('key'), Field.Store.YES))
            for ch in elem:
                if ch.text is None:
                    ch = etree.fromstring(self.htmlparser.unescape(etree.tostring(ch)))

                if ch.tag in FIELDS:
                    doc.add(TextField('content', ch.text, Field.Store.NO))
                else:
                    continue

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
            self.ndocs += 1
            if self.verbose and self.ndocs % 100000 == 0:
                print "%d documents processed..." % self.ndocs

            if DUMP_RANDOM_DOCS and self.ndocs in self.randdocs:
                self.extract_document(doc, self.randdocs.index(self.ndocs))

        except Exception, e:
            print "Indexing error:", e

    def complete_index(self):
        # self.writer.optimize()
        self.writer.close()
