import time
import lucene
import csv
import re
import json
from lxml import etree
from java.io import File
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import IndexReader, MultiFields
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version, BytesRefIterator
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from index import Indexer, CustomAnalyzer
from search import Searcher
from utils import check_config

INDEX_DIR = 'index'
DATA_DIR = 'data/dblp_small.xml'
QRELS_FIELDS = ['topic', 'iteration', 'document', 'relevancy']
CONFIG_DIR = 'config.json'
INDEX_EVAL_DIR = "eval/index_eval.txt"
TOPICS_DIR = "eval/topics.txt"
QRELS_DIR = "eval/qrels_manual/"
SEARCH_EVAL_DIR = "eval/search_eval.txt"


def evaluate_index(data_dir, store_dir, analyzer):
    """
    Evaluates vocabulary size and indexing speed for different
    analyzer configurations.
    """
    start = time.clock()
    Indexer(data_dir, store_dir, analyzer)
    end = time.clock()
    duration = end-start

    directory = SimpleFSDirectory(File(store_dir))
    reader = IndexReader.open(directory)
    vocabulary = MultiFields.getTerms(reader, 'title')
    vocab_size = vocabulary.size()

    # sometimes .size() doesn't return the correct size, in this case
    # we have to count manually
    if vocab_size == -1:
        termsref = BytesRefIterator.cast_(vocabulary.iterator(None))
        vocab_size = sum(1 for _ in termsref)

    reader.close()
    return duration, vocab_size


def evaluate_search(topics_dir, qrels_dir, searcher, N=0, k=10):
    """
    Evaluates the quality of search results.
    """
    scores = []
    queries = []
    tree = etree.parse(topics_dir)

    if N == 0:
        N = searcher.searcher.getIndexReader().numDocs()

    for element in tree.iter():
        if element.tag == 'num':
            topic_num = int(element.text)
        elif element.tag == 'query':
            print
            print("Evaluate topic %d") % topic_num
            gt = get_ground_truth(qrels_dir, topic_num)

            # perform search
            q = element.text
            queries.append(q)
            query, adv_query = parse_query(q)
            print "Standard query: %s" % query
            print "Advanced query: %s" % adv_query
            docs, _ = searcher.search(query=query, adv_query=adv_query, N=N)

            # get all ids from search results
            hits = []
            for doc in docs:
                d = searcher.searcher.doc(doc.doc)
                hits.append(str(d['id']))

            if len(hits) == 0:
                scores.append({'N': 0, 'k': k, 'nrelevant_gt': len(gt),
                               'precision': None, 'recall': None, 'f1': None,
                               'R-precision': None})
                continue

            P = []
            R = []
            F = []
            nretrieved = 0
            nrelevant = 0
            nrelevant_gt = len(gt)

            # calculate precision, recall and f1 score
            for hit in hits:
                nretrieved += 1
                nrelevant += min(1, sum([hit in d['document'] for d in gt]))
                prec = precision(nrelevant, nretrieved)
                rec = recall(nrelevant, nrelevant_gt)
                P.append(prec)
                R.append(rec)
                F.append(f1_score(prec, rec))
                if rec == 1:  # stop when all relevant documents are retrieved
                    break

            cutoff = min(k, nretrieved)
            if cutoff < 0:
                cutoff += nretrieved+1
            scores.append({'N': nretrieved, 'k': cutoff,
                           'nrelevant_gt': nrelevant_gt,
                           'precision': naround(P[cutoff-1]),
                           'recall': naround(R[cutoff-1]),
                           'f1': naround(F[cutoff-1]),
                           'R-precision': naround(P[min(len(P), nrelevant_gt)-1])})
    return scores, queries


def get_ground_truth(qrels_dir, topic_num):
    """
    Retrieves relevance judgments for given topic.
    """
    with open(qrels_dir + "qrels_%d" % topic_num) as f:
        reader = csv.reader(f, delimiter="\t")
        qrels = [dict(zip(QRELS_FIELDS, row)) for row in reader]
        gt = filter(lambda d: int(d['topic']) == topic_num and
                    int(d['relevancy']) == 1, qrels)
    return gt


def parse_query(q):
    """
    Parses test query and turn it into Lucene query.
    """
    if ':' in q:
        # parse advanced search options
        # standard query is everything before the first key
        query = ' '.join(q.split(":")[0].split(" ")[:-1])
        regex = re.compile(r"\b(\w+)\s*:\s*([^:]*)(?=\s+\w+\s*:|$)")
        adv_query = dict(regex.findall(q))
    else:
        # no advanced query, so everything is standard query
        query = q
        adv_query = None
    return query, adv_query


def precision(nrelevant, nretrieved):
    """
    Calculates precision metric.
    """
    if nretrieved == 0:
        return None

    return float(nrelevant)/nretrieved


def recall(nrelevant, nrelevant_gt):
    """
    Calculates recall metric.
    """
    if nrelevant_gt == 0:
        return None

    return float(nrelevant)/nrelevant_gt


def f1_score(precision, recall):
    """
    Calculates f1 score metric.
    """
    if precision is None or recall is None:
        return None
    if precision+recall == 0:
        return 0

    f1 = 2*(precision*recall)/(precision+recall)
    return f1


def naround(val, precision=4):
    """
    Rounds value if not None, otherwise returns None.
    """
    return round(val, precision) if val is not None else None


if __name__ == "__main__":
    lucene.initVM()

    # evaluate indexing options
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
    with open(INDEX_EVAL_DIR, 'w') as f:
        for config in configs:
            title_analyzer = CustomAnalyzer(config)
            per_field = HashMap()
            per_field.put("title", title_analyzer)
            analyzer = PerFieldAnalyzerWrapper(
                        StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
            duration, size = evaluate_index(DATA_DIR, INDEX_DIR, analyzer)
            print
            print(config)
            print("Speed of indexing: %.2fs" % round(duration, 2))
            print("Size of vocabulary on title attribute: %d\n" % size)

            f.write(str(config) + "\n")
            f.write("Speed of indexing: %.2fs\n" % round(duration, 2))
            f.write("Size of vocabulary on title attribute: %d\n" % size)

    # evaluate search
    # requires labeled test collection of documents in QRELS_DIR
    # to get meaningful results, one should first index the
    # test collection only by running build_index.py with EVAL_MODE=True

    print
    print("Evaluate search")
    scores = []
    N = 0

    # index documents
    with open(CONFIG_DIR) as f:
            config = json.load(f, encoding='ascii')
            config = check_config(config)

    title_analyzer = CustomAnalyzer(config['titleAnalyzer'])
    per_field = HashMap()
    per_field.put("title", title_analyzer)
    analyzer = PerFieldAnalyzerWrapper(
                StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
    searcher = Searcher(INDEX_DIR, analyzer, verbose=False)
    scores, queries = evaluate_search(TOPICS_DIR, QRELS_DIR, searcher,
                                      N=N, k=10)
    print
    print("Evaluation results:")
    with open(SEARCH_EVAL_DIR, 'w') as f:
        for i, q in enumerate(queries):
            print("%d) %s") % (i+1, q)
            print str(scores[i])

            f.write("%d) %s\n" % (i+1, q))
            f.write("%s\n" % scores[i])
