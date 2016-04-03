from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher, BooleanClause, \
     BooleanQuery
from org.apache.lucene.index import DirectoryReader
from java.io import File
import re
import time

FIELDS = ['title', 'authors', 'year', 'venue']


class Searcher():
    """
    Provides search functionality to retrieve documents to given user query.
    """
    def __init__(self, index_dir, analyzer, verbose=True):
        """
        Stores instances of Lucene searcher and analyzer.
        """
        directory = SimpleFSDirectory(File(index_dir))
        self.searcher = IndexSearcher(DirectoryReader.open(directory))
        self.analyzer = analyzer
        self.verbose = verbose

    def search(self, query='', adv_query=None, N=0):
        """
        Searches Lucene index to retrieve most relevant documents to given
        user query. Takes standard and advanced queries.
        """
        query = query.strip()
        search_query = BooleanQuery()

        # if query is empty, return nothing
        if query == '' and adv_query is None:
            return [], {'duration': 0, 'N': N, 'totalhits': 0}

        if self.verbose:
            if query != '':
                print "Searching for:", query
            if adv_query is not None:
                print "Searching for (advanced): ", adv_query

        # if 0, set N to max. number of documents in index to retrieve all docs
        N = self.searcher.getIndexReader().numDocs() if N == 0 else N

        # evaluate phrases of standard query on all fields
        if query != '':
            pq, query = self.extract_phrase_query(query, 'content')
            if pq is not None:
                # phrase queries have high priority
                search_query.add(pq, BooleanClause.Occur.MUST)

        # evaluate remaining keywords on all fields
        if query != '':
            q = QueryParser(Version.LUCENE_CURRENT, 'content',
                            self.analyzer).parse(query)
            search_query.add(q, BooleanClause.Occur.SHOULD)

        # evaluate advanced query options
        if adv_query is not None:
            for field, query in adv_query.iteritems():
                pq, query = self.extract_phrase_query(query, field)
                if pq is not None:
                    # phrase queries have high priority
                    search_query.add(pq, BooleanClause.Occur.MUST)

                if query != '':
                    q = QueryParser(Version.LUCENE_CURRENT, field,
                                    self.analyzer).parse(query)
                    # all advanced query options have high priority
                    search_query.add(q, BooleanClause.Occur.MUST)

        start = time.clock()
        topdocs = self.searcher.search(search_query, N)
        end = time.clock()
        duration = end-start
        metadata = {'duration': duration, 'N': N,
                    'totalhits': topdocs.totalHits}

        if self.verbose:
            print "Lucene query: " + str(search_query)
            self.show_results(topdocs.scoreDocs, metadata)

        return topdocs.scoreDocs, metadata

    def extract_phrase_query(self, q, field, slop=0, boost=5):
        """
        Extracts phrases from query and turns them into a Lucene query.
        """
        phrases = re.findall(r'"([^"]*)"', q)
        if len(phrases) == 0:
            return None, q

        q = re.sub(r'"([^"]*)"', "", q).strip()  # query without phrases
        if self.verbose:
            print "Detected phrases: ", phrases

        bq = BooleanQuery()
        for phrase in phrases:
            qparser = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer)
            # parse phrase - this may or may not be desired
            pq = qparser.parse('%s "%s"~%d^%.1f' %
                               (phrase, phrase, slop, boost))
            # phrase queries have high priority
            bq.add(pq, BooleanClause.Occur.MUST)

        return bq, q

    def run(self, N=0):
        """
        Provides text-based CLI to query search engine.
        """
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

    def show_results(self, results, metadata):
        """
        Prints results to stdout.
        """
        print "%d results found (%.2fs)" % \
            (metadata['totalhits'], metadata['duration'])
        print "Showing only top %d" % metadata['N']
        if len(results) > 0:
            results = self.format_results(results)
            print
            print "Result list:"

            for d in results:
                try:
                    # trying to convert doc into string might
                    # cause ascii error
                    print "%d) %s (relevance: %f)" % \
                        (d['rank'], d['key'], d['score'])
                    print d['title']
                    print d['authors']
                    print "%s - %s" % (str(d['venue']), str(d['year']))
                except UnicodeEncodeError, e:
                            print e

    def format_results(self, docs):
        """
        Formats result set.
        """
        results = []
        for (rank, doc) in enumerate(docs):
            d = self.searcher.doc(doc.doc)
            # snippet = searcher.retrieve_snippet(d['ee'])
            # if snippet is None:
            #     snippet = ''

            authors = ''
            for author in d.getValues('authors'):
                authors += author + ', '
            authors = authors[:-2]  # remove trailing comma and whitespace
            # remove trailing dot
            title = d['title'][:-1] if d['title'][-1] == "." else d['title']
            results.append(dict(rank=rank+1, score=round(doc.score, 2),
                                key=d['id'], title=title, authors=authors,
                                year=d['year'], venue=d['venue']))
        return results

    def search_year(self, q_year):
        """
        Retrieves all titles for a given year.
        """
        q = QueryParser(Version.LUCENE_CURRENT, 'year',
                        self.analyzer).parse(q_year)
        n_max = self.searcher.getIndexReader().numDocs()
        docs = self.searcher.search(q, n_max).scoreDocs
        titles = []
        for doc in docs:
            d = self.searcher.doc(doc.doc)
            titles.append(d['title'])
        return titles
