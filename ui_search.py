import lucene
import json
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap
from flask import Flask, render_template, request
import logging
import logging.handlers
from search import Searcher
from index import CustomAnalyzer
from utils import check_config

INDEX_DIR = 'index'
FIELDS = ['title', 'authors', 'year', 'venue']

# load config
with open('config.json') as f:
    config = json.load(f)
config = check_config(config)

# start JVM for Lucene
lucene.initVM()
vm_env = lucene.getVMEnv()

# use different analyzer for title field
title_analyzer = CustomAnalyzer(config['titleAnalyzer'])
per_field = HashMap()
per_field.put("title", title_analyzer)
analyzer = PerFieldAnalyzerWrapper(
            StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
searcher = Searcher(INDEX_DIR, analyzer)

# start Flask app
app = Flask(__name__, static_folder="web/static",
            template_folder="web/templates")
app.config.update(DEBUG=True)
logger = logging.getLogger('dblp-search')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)


@app.route('/')
def index():
    """
    Shows default view without any results.
    """
    return render_template('search.html')


@app.route('/search')
def search():
    """
    Performs search based on user-defined query and shows results.
    """
    vm_env.attachCurrentThread()
    query, adv_query = get_query()

    # ignore search if all fields are empty
    if query == '' and len(filter(None, adv_query.values())) == 0:
        return render_template('search.html', results=[], metadata=None,
                               query=query, adv_query=adv_query)

    docs, metadata = searcher.search(query=query, adv_query=adv_query,
                                     N=config['topN'])
    results = searcher.format_results(docs)
    return render_template('search.html', results=results, metadata=metadata,
                           query=query, adv_query=adv_query)


def get_query():
    """
    Retrieves user-defined query from search fields.
    """
    query = request.args.get('q', '').strip()
    title = request.args.get('title', '')
    authors = request.args.get('authors', '')
    year = request.args.get('year', '')
    venue = request.args.get('venue', '')
    values = [title, authors, year, venue]
    adv_query = dict(zip(FIELDS, [v.strip() for v in values]))
    return query, adv_query

if __name__ == '__main__':
    app.run()
