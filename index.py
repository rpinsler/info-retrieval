from java.io import File
from java.util import HashSet, Arrays
from org.apache.lucene.analysis.standard import StandardTokenizer, \
    StandardFilter
from org.apache.lucene.document import Document, StringField, TextField, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.pylucene.analysis import PythonAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import LowerCaseFilter, StopFilter, \
     StopAnalyzer
from org.apache.lucene.analysis.en import PorterStemFilter

from lxml import etree
import os
import random
import HTMLParser

TAGS = ('article', 'inproceedings')
HTML_TAGS = ('i', 'ref', 'sub', 'sup', 'tt')
FIELDS = ['title', 'author', 'year', 'journal', 'booktitle']
EVAL_MODE = True  # used to randomly sample documents for evaluation


class Indexer():
    """
    Provides functionality to parse and index the DBLP dataset.
    """

    def __init__(self, data_dir, store_dir, analyzer, verbose=True):
        """
        Sets up index writer and triggers indexing process.
        """
        if not os.path.exists(store_dir):
            os.mkdir(store_dir)

        store = SimpleFSDirectory(File(store_dir))
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        self.writer = IndexWriter(store, config)
        self.htmlparser = HTMLParser.HTMLParser()
        self.ndocs = 0
        self.verbose = verbose

        # sample some random documents for evaluation
        if EVAL_MODE:
            open("eval/qrels_manual/random_doc_selection", "w").close()
            open("eval/qrels_manual/qrels", "w").close()
            N = 3166933
            k = 150
            random.seed(0)
            self.randdocs = sorted(random.sample(range(1, N+1), k=k))
            f_coll = "eval/qrels_manual/testcollection"
            self.dblpdocs = [line.rstrip('\n') for line in open(f_coll)]
            self.collsize = 0
            self.dblpincoll = 0

        self.index(data_dir)
        self.writer.close()

        if self.verbose:
            print "Finished indexing. %d documents indexed in total." % \
                self.ndocs

    def index(self, data_dir):
        """
        Parses XML document and emits event for each matching tag. 
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
        """
        Indexes single record as Lucene document.
        """
        try:
            doc = Document()
            etree.strip_tags(elem, HTML_TAGS)  # remove HTML tags
            doc.add(StringField('id', elem.get('key'), Field.Store.YES))
            for ch in elem:
                if ch.text is None:
                    # unescape HTML characters if text is unreadable
                    ch = etree.tostring(ch)
                    ch = etree.fromstring(self.htmlparser.unescape(ch))

                # add text to content field to simplify standard queries
                if ch.tag in FIELDS:
                    doc.add(TextField('content', ch.text, Field.Store.NO))
                # elif ch.tag == 'ee':
                #     doc.add(StringField('ee', ch.text, Field.Store.YES))
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

            self.ndocs += 1
            if self.verbose and self.ndocs % 100000 == 0:
                print "%d documents processed..." % self.ndocs

            # add documents to test collection
            if EVAL_MODE:
                dblp_missing = len(self.dblpdocs)-self.dblpincoll
                if doc['id'] in self.dblpdocs:
                    self.extract_document(doc)
                    self.dblpincoll += 1
                    self.writer.addDocument(doc)
                elif (self.ndocs in self.randdocs) and \
                     (self.collsize + dblp_missing < 300):
                    # add random document to test collection as long as results
                    # from DBLP search API still fit in
                    self.extract_document(doc)
                    self.writer.addDocument(doc)
                return

            self.writer.addDocument(doc)

        except Exception, e:
            print "Indexing error:", e

    def extract_document(self, doc):
        """
        Extracts values from Lucene document and writes them into
        relevance judgments template file.
        """
        with open("eval/qrels_manual/random_doc_selection", "a") as f:
            # have to be careful with the correct encoding here!
            self.collsize += 1
            f.write('%d) ' % (self.collsize))
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


class CustomAnalyzer(PythonAnalyzer):
    """
    Allows to configure analyzer. Currently, uses PorterStemmer for stemming
    and default stopword list for stopword removal. However, this could be
    easily extended in the future.
    """
    def __init__(self, config):
        """
        Extracts and stores configuration values.
        """
        self.lowercase = config['lowercase']
        self.stemming = config['stemming']
        self.stopwords = config['stopwords']
        PythonAnalyzer.__init__(self)

    def createComponents(self, fieldName, reader):
        """
        Composes analyzer by adding filters according to config.
        """
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
