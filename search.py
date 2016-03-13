from org.apache.lucene.queryparser.classic import QueryParser, \
     MultiFieldQueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from java.io import File
import re
import time


class Searcher():
    def __init__(self, index_dir, analyzer):
        directory = SimpleFSDirectory(File(index_dir))
        self.searcher = IndexSearcher(DirectoryReader.open(directory))
        self.analyzer = analyzer

    def search(self, user_query, fields=[''], N=0):
        # TODO: support double quotation marks for phrases (e.g. "event detection")
        print "Searching for: ", user_query
        # phrases = re.findall(r'"([^"]*)"', user_query)
        # q = re.sub(r'"([^"]*)"', "", user_query)
        # print "Detected phrases: ", phrases
        # p = PhraseQuery()
        # for phrase in phrases:
        #   p.add(Term(somefield, phrase)

        if fields == ['']:
            fields = ['title', 'authors', 'year', 'venue']

        print
        print "Searching in fields: ", fields
        q = user_query
        parser = MultiFieldQueryParser(Version.LUCENE_CURRENT, fields,
                                       self.analyzer)
        query = MultiFieldQueryParser.parse(parser, q)
        print query
        start = time.clock()
        docs = self.searcher.search(query, N).scoreDocs
        end = time.clock()
        duration = end-start
        print "%s total matching documents." % len(docs)
        for doc in docs:
            d = self.searcher.doc(doc.doc)
            try:
                print(d)  # might return ascii error when converting to string
            except Exception, e:
                        print e

        # return top N results along with rank, scores, docID and snippets
        return docs, duration

    def run(self, N=0):
        while True:
            print
            print "Hit enter with no input to quit."
            user_query = raw_input("Query: ")
            if user_query == '':
                return
            print

            fields = raw_input("Fields to search through (comma separated): ")
            fields = fields.split(",")
            self.search(user_query, fields, N)
