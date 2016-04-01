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
import urllib
import lxml
from lxml import html

FIELDS = ['title', 'authors', 'year', 'venue']


class Searcher():
    def __init__(self, index_dir, analyzer, verbose=True):
        directory = SimpleFSDirectory(File(index_dir))
        self.searcher = IndexSearcher(DirectoryReader.open(directory))
        self.analyzer = analyzer
        self.verbose = verbose

    def search(self, query='', adv_query=None, N=0, searchafter=None):
        query = query.strip()
        search_query = BooleanQuery()

        if query == '' and adv_query is None:
            return [], 0

        if self.verbose:
            if query != '':
                print "Searching for:", query
            if adv_query is not None:
                print "Searching for (advanced): ", adv_query

        if N == 0:
            N = self.searcher.getIndexReader().numDocs()

        # evaluate phrases of standard query on all fields
        if query != '':
            pq, q = self.extract_phrase_query(query, 'content')
            if pq is not None:
                # phrase queries have high priority
                search_query.add(pq, BooleanClause.Occur.MUST)
            query = q

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

        # implement some basic paging
        if searchafter is not None:
            topdocs = self.searcher.searchAfter(searchafter, search_query,
                                                N).scoreDocs
        else:
            topdocs = self.searcher.search(search_query, N)

        end = time.clock()
        duration = end-start
        docs = topdocs.scoreDocs
        metadata = {'duration': duration, 'N': N,
                    'totalhits': topdocs.totalHits}

        if self.verbose:
            print "Lucene query: " + str(search_query)
            self.show_results(docs, metadata)

        return docs, metadata

    def extract_phrase_query(self, q, field, slop=0, boost=5):
        phrases = re.findall(r'"([^"]*)"', q)
        if len(phrases) == 0:
            return None, q

        q = re.sub(r'"([^"]*)"', "", q).strip()  # query without phrases
        if self.verbose:
            print "Detected phrases: ", phrases

        bq = BooleanQuery()
        for phrase in phrases:
            # pq = PhraseQuery()
            # for term in filter(None, phrase.split(' ')):
            #     pq.add(Term(field, term))
            qparser = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer)
            # parse phrase - this may or may not be desired
            # pq = qparser.parse(field + ':"' + phrase + '"')
            # pq = qparser.parse('%s "%s"~%d^%.1f' %
            # pq = qparser.parse('%s "%s"~%d^%.1f' %
            #                   (phrase, phrase, slop, boost))
            pq = qparser.parse('%s "%s"~%d^%.1f' %
                               (phrase, phrase, slop, boost))
            # phrase queries have high priority
            bq.add(pq, BooleanClause.Occur.MUST)
            # bq.add(pq, BooleanClause.Occur.SHOULD)

        return bq, q

    def search_year(self, q_year):
        search_query = BooleanQuery()
        q = QueryParser(Version.LUCENE_CURRENT, 'content',
                        self.analyzer).parse(q_year)
        search_query.add(q, BooleanClause.Occur.MUST)
        docs = self.searcher.search(search_query, 0x7fffffff).scoreDocs
        titles = []
        for doc in docs:
            d = self.searcher.doc(doc.doc)
            titles.append(d.get('title'))
        return titles

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

    def show_results(self, results, metadata):
        print "%d results found (%.2fs)" % \
            (metadata['totalhits'], metadata['duration'])
        print "Showing only top %d" % metadata['N']
        if len(results) > 0:
            print
            print "Result list:"

            for i, doc in enumerate(results):
                d = self.searcher.doc(doc.doc)
                try:
                    # trying to convert doc into string might
                    # cause ascii error
                    # print str(i+1) + ") " + str(d)
                    authors = ''
                    for author in d.getValues('authors'):
                        authors += author.encode("utf-8") + ', '
                    authors = authors[:-2]
                    print "%d) %s (relevance: %.2f)" % (i, d['id'], doc.score)
                    print "%s - %s - %s" % (authors, str(d['venue']), str(d['year']))
                    print "some snippet...."
                except UnicodeEncodeError, e:
                            print e

    def retrieve_snippet(self, docurl):
        # import pdb; pdb.set_trace()
        if docurl == None:
            return None
        response = urllib.urlopen(docurl)
        doc = lxml.html.parse(response).getroot()
        abstract = doc.find_class('abstract')
        if len(abstract) == 0:
            abstract = doc.find_class('Abstract')
        else:
            abstract = abstract[0]
        if len(abstract) == 0:
            abstract = doc.get_element_by_id("abstract", None)
        else:
            abstract = abstract[0]
        if abstract is None:
            abstract = doc.get_element_by_id("Abstract", None)
        if abstract is None:
            elements = doc.xpath("//p")
            if len(elements) == 0:
                return None
            lens = [len(elem.text) if elem.text is not None else 0 for elem in elements]
            abstract = [elements[lens.index(max(lens))]]
        else:
            return None

        for elem in abstract:
            if elem.tag == 'p':
                return elem.text[:150] + "..."
        return None
