from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, FieldInfo
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

from lxml import etree


class Indexer():
    def __init__(self, index_dir, context):
        store = SimpleFSDirectory(File(index_dir))
        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
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
        # index at least the following attributes:
        # - paper id (or key)
        # - paper title
        # - authors
        # - year of publication
        # - publication venue: journal for article, booktitle for inproceedings

        # TODO: (optionally) perform stemming on title
        # TODO: (optionally) perform lower case conversion on title
        # TODO: (optionally) use stopwords on title

        # TODO: set indexing options properly
        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)

        try:
            doc = Document()
            # remove <i></i> tags that are sometimes used in titles
            etree.strip_tags(elem, 'i')
            doc.add(Field('id', elem.get('key'), t1))
            for ch in elem:
                if ch.tag == 'title':
                    doc.add(Field('title', ch.text, t1))
                elif ch.tag == 'author':
                    pass
                    # how to add multiple entries to same field?
                    # entry.setdefault('authors', []).append(ch.text)
                elif ch.tag == 'year':
                    doc.add(Field('year', ch.text, t1))
                elif ch.tag == 'journal' or ch.tag == 'booktitle':
                    doc.add(Field('venue', ch.text, t1))

            self.writer.addDocument(doc)
        except Exception, e:
            print "Indexing error:", e

    def complete_index(self):
        # self.writer.optimize()
        self.writer.close()
