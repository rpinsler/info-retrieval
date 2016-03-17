from org.apache.lucene.queryparser.classic import QueryParser, \
     MultiFieldQueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher, BooleanClause, \
     BooleanQuery, PhraseQuery
from org.apache.lucene.index import DirectoryReader, Term
from java.io import File
import re
import time

FIELDS = ['title', 'authors', 'year', 'venue']


class Searcher():
    def __init__(self, index_dir, analyzer):
        directory = SimpleFSDirectory(File(index_dir))
        self.searcher = IndexSearcher(DirectoryReader.open(directory))
        self.analyzer = analyzer

    def search(self, query='', adv_query=None, N=0):
        query = query.strip()
        search_query = BooleanQuery()

        if query == '' and adv_query is None:
            return [], 0, search_query

        if query != '':
            print "Searching for:", query
        if adv_query is not None:
            print "Searching for (advanced): ", adv_query

        # evaluate phrases of standard query for title field
        if query != '':
            pq, query = self.extract_phrase_query(query, "title")
            if pq is not None:
                # phrase queries have high priority
                search_query.add(pq, BooleanClause.Occur.MUST)

        # evaluate remaining keywords on all fields
        if query != '':
            mfqparser = MultiFieldQueryParser(Version.LUCENE_CURRENT, FIELDS,
                                              self.analyzer)
            mfq = MultiFieldQueryParser.parse(mfqparser, query)
            search_query.add(mfq, BooleanClause.Occur.SHOULD)

        # evaluate advanced query options
        if adv_query is not None:
            for field, query in adv_query.iteritems():
                if field == 'title':
                    pq, query = self.extract_phrase_query(query, field)
                    if pq is not None:
                        # phrase queries have high priority
                        search_query.add(pq, BooleanClause.Occur.MUST)

                if query != '':
                    q = QueryParser(Version.LUCENE_CURRENT, field,
                                    self.analyzer).parse(query)
                    # all advanced query options have high priority
                    search_query.add(q, BooleanClause.Occur.MUST)

        print "Lucene query: " + str(search_query)
        start = time.clock()
        docs = self.searcher.search(search_query, N).scoreDocs
        end = time.clock()
        duration = end-start
        print "%s total matching document(s)." % len(docs)
        if len(docs) > 0:
            print
            print "Result list:"
        for i, doc in enumerate(docs):
            d = self.searcher.doc(doc.doc)
            try:
                # trying to convert doc into string might cause ascii error
                print str(i+1) + ") " + str(d)
            except Exception, e:
                        print e

        # return top N results along with rank, scores, docID and snippets
        return docs, duration

    def extract_phrase_query(self, q, field):
        phrases = re.findall(r'"([^"]*)"', q)
        if len(phrases) == 0:
            return None, q

        q = re.sub(r'"([^"]*)"', "", q).strip()  # query without phrases
        print "Detected phrases: ", phrases

        bq = BooleanQuery()
        for phrase in phrases:
            # pq = PhraseQuery()
            # for term in filter(None, phrase.split(' ')):
            #     pq.add(Term(field, term))
            qparser = QueryParser(field, self.analyzer)
            pq = qparser.parse(field + ':"' + phrase + '"')
            # phrase queries have high priority
            bq.add(pq, BooleanClause.Occur.MUST)

        return bq, q

    def run(self, N=0):
        while True:
            print
            print "Standard search. Type ':q' to quit."
            query = raw_input("Query: ")
            if query == ':q':
                return
            print

            b_adv = raw_input("Use advanced search? (y/n): ")
            adv_query = None
            if b_adv == 'y':
                print "Advanced search. Hit enter with no input to skip field."
                title = raw_input("Title: ")
                authors = raw_input("Authors: ")
                year = raw_input("Year: ")
                venue = raw_input("Venue: ")
                values = [title, authors, year, venue]
                if filter(None, values) != []:
                    adv_query = dict(zip(FIELDS, values))

            elif b_adv == 'n':
                print "Proceed without advanced search."
            else:
                print "Invalid input. Proceed without advanced search."

            print
            print "Execute search."

            self.search(query, adv_query, N)
