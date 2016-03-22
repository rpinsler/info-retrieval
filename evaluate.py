import time
import os
import lucene
import csv
from lxml import etree
from java.io import File
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import IndexReader, MultiFields
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap

from index import Indexer, CustomAnalyzer
from search import Seacher

INDEX_DIR = 'index'
# DATA_DIR = 'data/dblp.xml'
DATA_DIR = 'data/dblp_small.xml'
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
    # print str(vocabulary.size()) # size of vocabulary
    # print str(vocabulary.getDocCount()) # #docs that have at least one term for title field
    # print str(vocabulary.getSumTotalTermFreq()) # #tokens
    # print str(vocabulary.getSumDocFreq()) # #postings

    vocab_size = vocabulary.size()
    reader.close()
    return duration, vocab_size


def evaluate_search(topics_dir, qrels_dir, searcher, ndocs=0, N=0):
    scores = []
    tree = etree.parse("eval/topics")

    # get ground truth
    with open(qrels_dir) as f:
        reader = csv.reader(f, delimiter="\t")
        qrels = [dict(zip(QRELS_FIELDS, row)) for row in reader]

    for element in tree.iter():
        # get topic information
        if element.tag == 'num':
            topic_num = int(element.text)
        elif element.tag == 'query':
            gt = filter(lambda d: int(d['topic']) == topic_num and
                        int(d['relevancy']), qrels)
            if ndocs != 0:
                # fill up with placeholder values for non-relevant docs
                gt.append([dict(zip(QRELS_FIELDS, [topic_num, 0, '', 0]))] *
                          ndocs-len(gt))
            # perform search
            q = element.text
            docs = searcher.search(query=q, adv_query=None, N)
            hits = []
            for doc in docs:
                d = searcher.searcher.doc(doc.doc)
                hits.append(d['id'])

            nretrieved = len(hits)
            nrelevant = len(filter(lambda d: d in gt, hits))
            nrelevant_gt = len(gt)
            prec = precision(nrelevant, nretrieved)
            rec = recall(nrelevant, nrelevant_gt)
            f1 = f1_score(prec, rec)
            scores.append({'N': N, 'nrelevant_gt': nrelevant_gt,
                           'precision': prec, 'recall': rec, 'f1': f1})
    return scores


def precision(nrelevant, nretrieved):
    if nretrieved == 0:
        return None

    return nrelevant/nretrieved


def recall(nrelevant, nrelevant_gt):
    if nrelevant_gt == 0:
        return None

    return nrelevant/nrelevant_gt


def f1_score(precision, recall):
    if precision is None or recall is None:
        return None
    if precision+recall == 0:
        return 0

    f1 = 2*(precision*recall)/(precision+recall)
    return f1

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
