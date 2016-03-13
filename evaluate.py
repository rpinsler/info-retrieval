import time
import os
import lucene
from lxml import etree
from java.io import File
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import IndexReader, MultiFields
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from index import Indexer, CustomAnalyzer

INDEX_DIR = 'index'
# DATA_DIR = 'data/dblp.xml'
DATA_DIR = 'data/dblp_small.xml'


def evaluate_index(index_dir, context, analyzer):
    # eval time of indexing (overall)
    # we should also measure the elapsed time of
    # each index_document call seperately
    start = time.clock()
    Indexer(index_dir, context, analyzer)
    end = time.clock()
    duration = end-start

    directory = SimpleFSDirectory(File(index_dir))
    reader = IndexReader.open(directory)
    vocabulary = MultiFields.getTerms(reader, 'title')
    # print str(vocabulary.size()) # size of vocabulary
    # print str(vocabulary.getDocCount()) # #docs that have at least one term for title field
    # print str(vocabulary.getSumTotalTermFreq()) # #tokens
    # print str(vocabulary.getSumDocFreq()) # #postings

    vocab_size = vocabulary.size()
    reader.close()
    return duration, vocab_size


def evaluate_search(queries, gt, searcher, analyzer, N):
    scores = []
    for q in queries:
        docs = search(q, searcher, analyzer, N)
        prec = precision(docs, gt)
        rec = recall(docs, gt)
        f1 = f1_score(docs, gt)
        scores.append({'precision': prec, 'recall': rec, 'f1': f1})
    return scores


def precision(docs, gt):
    pass


def f1_score(docs, gt):
    pass


def recall(docs, gt):
    pass

if __name__ == "__main__":
    base_dir = os.path.expanduser("~") + "/Semester_NTU/" + \
               "10 Information Retrieval and Analysis/info-retrieval"
    lucene.initVM()

    configs = [{'lowercase': False, 'stemming': False, 'stopwords': False},
               {'lowercase': False, 'stemming': False, 'stopwords': True},
               {'lowercase': False, 'stemming': True, 'stopwords': False},
               {'lowercase': False, 'stemming': True, 'stopwords': True},
               {'lowercase': True, 'stemming': False, 'stopwords': False},
               {'lowercase': True, 'stemming': False, 'stopwords': True},
               {'lowercase': True, 'stemming': True, 'stopwords': False},
               {'lowercase': True, 'stemming': True, 'stopwords': True}]

    print
    print("Evaluate indexing options")
    for config in configs:
        context = etree.iterparse(DATA_DIR, events=('end',),
                                  tag=('article', 'inproceedings'),
                                  dtd_validation=True)
        title_analyzer = CustomAnalyzer(config)
        per_field = HashMap()
        per_field.put("title", title_analyzer)
        analyzer = PerFieldAnalyzerWrapper(
                    StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
        duration, size = evaluate_index(os.path.join(base_dir, INDEX_DIR),
                                        context, analyzer)
        print
        print(config)
        print("Speed of indexing: " + str(round(duration, 2)) + "s")
        print("Size of vocabulary on title attribute: " + str(size))
