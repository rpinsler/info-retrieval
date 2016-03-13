import lucene
import os
import sys
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap
from flask import Flask, render_template, request
import logging
import logging.handlers

base_dir = os.path.expanduser("~") + "/Semester_NTU/" + \
           "10 Information Retrieval and Analysis/info-retrieval"
sys.path.insert(0, base_dir)
from search import Searcher
from index import CustomAnalyzer

INDEX_DIR = 'index'

lucene.initVM()
vm_env = lucene.getVMEnv()
config = {'lowercase': False, 'stemming': True, 'stopwords': True}
title_analyzer = CustomAnalyzer(config)
per_field = HashMap()
per_field.put("title", title_analyzer)
analyzer = PerFieldAnalyzerWrapper(
            StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
searcher = Searcher(os.path.join(base_dir, INDEX_DIR), analyzer)

app = Flask(__name__)
app.config.update(
    DEBUG=True,
)

logger = logging.getLogger('kumologging')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/search')
def search():
    vm_env.attachCurrentThread()
    user_query = request.args.get('q', '')
    if user_query == '':
        return render_template('search.html', results=[], metadata=None, query=user_query)

    docs, duration = searcher.search(user_query, N=10)
    lipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse laoreet mauris eu tortor" + \
    		 "interdum tempor. Sed vulputate odio odio. Sed arcu neque, accumsan et urna quis, ultrices" + \
    		 "consectetur turpis. Donec eu euismod sem, nec aliquam velit. Donec ac tristique mi."
    # docs = [['Some interesting title', 'text', 1, 13.37, "this/is/some/key", "Bruce Lee and Jackie Chan", 2002, "SIGIR"],
    # 		['Another title', 'moretext', 2, 4.04, "yet/another/key", "John Doe", 2014, "WISDM"],
    # 		['It is all about the title', 'notext', 3, 1.01, "the/key/is/key", "Adam Smith", 1983, "KDD"]]
    results = []
    for (rank, doc) in enumerate(docs):
        d = searcher.searcher.doc(doc.doc)
        results.append(dict(rank=rank+1, score=round(doc.score, 2),
                            key=d.get('id'), title=d.get('title'), text=lipsum,
                            authors=d.get('authors'),
                            year=d.get('year'), venue=d.get('venue')))
    # results = [dict(title=doc[0], text=lipsum, rank=doc[2], score=doc[3],
    #            key=doc[4], authors=doc[5], year=doc[6], venue=doc[7])
    #            for doc in docs]
    metadata = dict(time=round(duration, 2))
    return render_template('search.html', results=results, metadata=metadata, query=user_query)

if __name__ == '__main__':
    app.run()
