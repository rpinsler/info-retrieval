from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.util import Version

# this should probably be turned into a class like Indexer in index.py


def search(q, searcher, analyzer, N):
    # TODO: allow free text keyword queries on any attributes
    # TODO: parameterize freetext search on specific attributes
    # TODO: support double quotation marks for phrases (e.g. "event detection")
    # (currently hard-coded as 'year')
    query = QueryParser(Version.LUCENE_CURRENT, 'year', analyzer).parse(q)
    docs = searcher.search(query, N).scoreDocs
    # print "%s total matching documents." % len(docs)
    for doc in docs:
        d = searcher.doc(doc.doc)
        try:
            print(d)  # might return ascii error when converting to string
        except Exception, e:
            print e

    # return top N results along with rank, scores, docID and snippets
    return docs
