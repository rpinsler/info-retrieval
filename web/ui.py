import lucene
import os
import sys
import json
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
from utils import check_config

INDEX_DIR = 'index'
FIELDS = ['title', 'authors', 'year', 'venue']

with open('config.json') as f:
    config = json.load(f)
config = check_config(config)

lucene.initVM()
vm_env = lucene.getVMEnv()
title_analyzer = CustomAnalyzer(config['titleAnalyzer'])
per_field = HashMap()
per_field.put("title", title_analyzer)
analyzer = PerFieldAnalyzerWrapper(
            StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
searcher = Searcher(os.path.join(base_dir, INDEX_DIR), analyzer)

app = Flask(__name__)
app.config.update(
    DEBUG=True,
)

logger = logging.getLogger('dblp-search')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/search')
def search():
    vm_env.attachCurrentThread()
    query = request.args.get('q', '').strip()
    title = request.args.get('title', '').strip()
    authors = request.args.get('authors', '').strip()
    year = request.args.get('year', '').strip()
    venue = request.args.get('venue', '').strip()
    values = [title, authors, year, venue]
    adv_query = dict(zip(FIELDS, values))
    if query == '' and len(filter(None, values)) == 0:
        return render_template('search.html', results=[], metadata=None,
                               query=query, adv_query=adv_query)

    docs, duration = searcher.search(query=query, adv_query=adv_query, N=config['topN'])
    lipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse laoreet mauris eu tortor" + \
    		 "interdum tempor. Sed vulputate odio odio. Sed arcu neque, accumsan et urna quis, ultrices" + \
    		 "consectetur turpis. Donec eu euismod sem, nec aliquam velit. Donec ac tristique mi."
    # docs = [['Some interesting title', 'text', 1, 13.37, "this/is/some/key", "Bruce Lee and Jackie Chan", 2002, "SIGIR"],
    # 		['Another title', 'moretext', 2, 4.04, "yet/another/key", "John Doe", 2014, "WISDM"],
    # 		['It is all about the title', 'notext', 3, 1.01, "the/key/is/key", "Adam Smith", 1983, "KDD"]]
    results = []
    for (rank, doc) in enumerate(docs):
        d = searcher.searcher.doc(doc.doc)
        authors = ''
        for author in d.getValues('authors'):
            authors += author.encode("utf-8") + ', '
        authors = authors[:-2]
        results.append(dict(rank=rank+1, score=round(doc.score, 2),
                            key=d['id'], title=d['title'][:-1], text=lipsum,
                            authors=authors,
                            year=d['year'], venue=d['venue']))
    metadata = dict(time=round(duration, 2))
    return render_template('search.html', results=results, metadata=metadata,
                           query=query, adv_query=adv_query)

if __name__ == '__main__':
    app.run()
