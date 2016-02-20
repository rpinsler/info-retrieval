import time
import search


def evaluate_index(Indexer, *args, **kwargs):
    # eval time of indexing (overall)
    # we should also measure the elapsed time of
    # each index_document call seperately
    start = time.clock()
    Indexer(*args, **kwargs)
    end = time.clock()
    duration = end-start

    # TODO: get vocabulary size
    vocab_size = None

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
