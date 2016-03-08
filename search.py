from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser
from org.apache.lucene.util import Version

# this should probably be turned into a class like Indexer in index.py


def search(q, fields, searcher, analyzer, N):
    # TODO: support double quotation marks for phrases (e.g. "event detection")
    if fields is None:
        fields = ['title', 'authors', 'year', 'venue']
    parser = MultiFieldQueryParser(Version.LUCENE_CURRENT, fields, analyzer)
    query = MultiFieldQueryParser.parse(parser, q)
    # query = QueryParser(Version.LUCENE_CURRENT, 'title', analyzer).parse(q)
    docs = searcher.search(query, N).scoreDocs
    print "%s total matching documents." % len(docs)
    for doc in docs:
        d = searcher.doc(doc.doc)
        try:
            print(d)  # might return ascii error when converting to string
        except Exception, e:
            print e

    # return top N results along with rank, scores, docID and snippets
    return docs


def run(searcher, analyzer, N):
    while True:
        print
        print "Hit enter with no input to quit."
        user_query = raw_input("Query: ")
        if user_query == '':
            return
        print
        print "Searching for: ", user_query
        phrases = re.findall(r'"([^"]*)"', user_query)
        q = re.sub(r'"([^"]*)"', "", user_query)
        print "Detected phrases: ", phrases

        # p = PhraseQuery()
        # for phrase in phrases:
        #   p.add(Term(somefield, phrase)

        fields = raw_input("Fields to search through (comma separated list): ")
        if fields == '':
            fields = ['title', 'authors', 'year', 'venue']
        else:
            fields = fields.split(",")

        print
        print "Searching in fields: ", fields
        parser = MultiFieldQueryParser(Version.LUCENE_CURRENT, fields, analyzer)
        query = MultiFieldQueryParser.parse(parser, q)
        print query
        docs = searcher.search(query, N).scoreDocs
        print "%s total matching documents." % len(docs)
        for doc in docs:
            d = searcher.doc(doc.doc)
            try:
                print(d)  # might return ascii error when converting to string
            except Exception, e:
                print e
