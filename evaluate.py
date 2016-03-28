import time
import os
import lucene
import csv
import re
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

INDEX_DIR = 'index'
DATA_DIR = 'data/dblp.xml'
# DATA_DIR = 'data/dblp_small.xml'
QRELS_FIELDS = ['topic', 'iteration', 'document', 'relevancy']


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
    vocab_size = vocabulary.size()
    if vocab_size == -1:
        termsref = BytesRefIterator.cast_(vocabulary.iterator(None))
        vocab_size = sum(1 for _ in termsref)


    # print str(vocab_size) # size of vocabulary
    # print str(vocabulary.getDocCount()) # #docs that have at least one term for title field
    # print str(vocabulary.getSumTotalTermFreq()) # #tokens
    # print str(vocabulary.getSumDocFreq()) # #postings

    reader.close()
    return duration, vocab_size


def evaluate_search(topics_dir, qrels_dir, searcher, N=0, k=[10]):
    scores = []
    tree = etree.parse(topics_dir)

    if N == 0:
        N = searcher.searcher.getIndexReader().numDocs()
    if not isinstance(k, list):
        k = [k]

    for element in tree.iter():
        # get topic information
        if element.tag == 'num':
            topic_num = int(element.text)
            # get ground truth
        elif element.tag == 'query':
            print("Evaluate topic %d") % topic_num
            with open(qrels_dir + "qrels_%d" % topic_num) as f:
                reader = csv.reader(f, delimiter="\t")
                qrels = [dict(zip(QRELS_FIELDS, row)) for row in reader]
                gt = filter(lambda d: int(d['topic']) == topic_num and
                            int(d['relevancy']) == 1, qrels)
                # perform search
                q = element.text
                if ':' in q:
                    query = ' '.join(q.split(":")[0].split(" ")[:-1])
                    regex = re.compile(r"\b(\w+)\s*:\s*([^:]*)(?=\s+\w+\s*:|$)")
                    adv_query = dict(regex.findall(q))
                else:
                    query = q
                    adv_query = None
                print query
                print adv_query
                docs, _ = searcher.search(query=query, adv_query=adv_query, N=N)
                hits = []
                for doc in docs:
                    d = searcher.searcher.doc(doc.doc)
                    hits.append(str(d['id']))

                P = []
                R = []
                F = []
                nretrieved = 0
                nrelevant = 0
                nrelevant_gt = len(gt)

                if len(hits) == 0:
                    scores.append({'N': nretrieved, 'k': k[0], 'nrelevant_gt': nrelevant_gt,
                                   'precision': None, 'recall': 0, 'f1': None})

                for hit in hits:
                    nretrieved += 1
                    nrelevant += min(1, sum([hit in d['document'] for d in gt]))
                    prec = precision(nrelevant, nretrieved)
                    rec = recall(nrelevant, nrelevant_gt)
                    P.append(prec)
                    R.append(rec)
                    F.append(f1_score(prec, rec))
                    if rec == 1:
                        break

                k[0] = min(k[0], nretrieved)
                for cutoff in k:
                    if cutoff > nretrieved:
                        break
                    if cutoff < 0:
                        cutoff += nretrieved+1
                    scores.append({'N': nretrieved, 'k': cutoff, 'nrelevant_gt': nrelevant_gt,
                                   'precision': naround(P[cutoff-1]), 'recall': naround(R[cutoff-1]),
                                   'f1': naround(F[cutoff-1])})
    return scores


def precision(nrelevant, nretrieved):
    if nretrieved == 0:
        return None

    return float(nrelevant)/nretrieved


def recall(nrelevant, nrelevant_gt):
    if nrelevant_gt == 0:
        return None

    return float(nrelevant)/nrelevant_gt


def f1_score(precision, recall):
    if precision is None or recall is None:
        return None
    if precision+recall == 0:
        return 0

    f1 = 2*(precision*recall)/(precision+recall)
    return f1


def naround(val, precision=4):
    return round(val, precision) if val is not None else None

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

#    print
#    print("Evaluate indexing options")
#    with open("eval/index_eval.txt", 'w') as f:
#        for config in configs:
#            context = etree.iterparse(DATA_DIR,
#                                      events=('end',),
#                                      tag=('article', 'inproceedings'),
#                                      dtd_validation=True)
#            title_analyzer = CustomAnalyzer(config)
#            per_field = HashMap()
#            per_field.put("title", title_analyzer)
#            analyzer = PerFieldAnalyzerWrapper(
#                        StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
#            duration, size = evaluate_index(os.path.join(base_dir, INDEX_DIR),
#                                            context, analyzer)
#            print
#            print(config)
#            print("Speed of indexing: %.2fs" % round(duration, 2))
#            print("Size of vocabulary on title attribute: %d\n" % size)
#
#            f.write(str(config) + "\n")
#            f.write("Speed of indexing: %.2fs\n" % round(duration, 2))
#            f.write("Size of vocabulary on title attribute: %d\n" % size)

    print
    print("Evaluate search")
    topics_dir = "eval/topics"
    qrels_dir = "eval/qrels_dblp/"
    scores = []
    N = 0

    # index documents
    config = {'lowercase': True, 'stemming': True, 'stopwords': True}
    title_analyzer = CustomAnalyzer(config)
    per_field = HashMap()
    per_field.put("title", title_analyzer)
    analyzer = PerFieldAnalyzerWrapper(
                StandardAnalyzer(Version.LUCENE_CURRENT), per_field)
    searcher = Searcher(INDEX_DIR, analyzer, verbose=False)
    scores = evaluate_search(topics_dir, qrels_dir, searcher, N=N, k=[10,-1])
    for i, sc in enumerate(scores):
        print("%d) %s") % (i+1, sc)

    # problem with topic 3: doesnt find second hit due to lack of stemming
    # problem with topics 5,8,9: if system occurs multiple times, it counts more
