from lxml import etree
import urllib
import re
import os

RECORD_TYPES = ["Conference and Workshop Papers", "Journal Articles"]
API_URL = "http://dblp.uni-trier.de/search/publ/api?"
QRELS_DIR = "eval/qrels_dblp/"
DBLP_RESULTS_DIR = "eval/qrels_dblp/dblp_results.txt"
TOPICS_DIR = "eval/topics.txt"


def parse(context):
    """
    Parses results from DBLP search API.
    Based on Liza Daly's fast_iter
    http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    See also http://effbot.org/zone/element-iterparse.htm
    """
    for _, hits in context:
        nresults = int(hits.get('total'))

    res = []
    for elem in hits:
        score = int(elem.get('score'))
        key = parse_element(elem)
        if key is not None:
            res.append({'key': key, 'score': score})

        # It's safe to call clear() here because no descendants will be
        # accessed
        elem.clear()
        # Also eliminate now-empty references from the root node to elem
        for ancestor in elem.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
    del context
    return res, nresults


def parse_element(elem):
    """
    Extracts key from result if is of the right record type.
    """
    key = None
    try:
        for el in elem:
            if el.tag == "info":
                for ch in el:
                    key = None
                    if ch.tag == 'type' and ch.text not in RECORD_TYPES:
                        return None
                    elif ch.tag == 'url':
                        key = ch.text[20:]

    except Exception, e:
        print "Parse error:", e
    return key


def build_dblp_query(q):
    q = q.replace('authors', 'author')
    phrases = re.findall(r'"([^"]*)"', q)
    for phrase in phrases:
        p = phrase.replace('"', '').replace(' ', '.')
        q = q.replace('"%s"' % phrase, p)
    return q

if __name__ == "__main__":
    tree = etree.parse(TOPICS_DIR)
    results = []
    if not os.path.exists(QRELS_DIR):
        os.mkdir(QRELS_DIR)

    for element in tree.iter():
        if element.tag == 'num':
            topic_num = int(element.text)
        elif element.tag == 'query':
            data_dir = QRELS_DIR + 'q_%d.txt' % topic_num
            open(QRELS_DIR + "qrels_%d.txt" % topic_num, 'w').close()
            nretrieved = 0
            nresults = 1000
            nfetch = 1000
            maxscore = 0
            while nretrieved < nresults:
                q = element.text
                q = build_dblp_query(q)
                query = urllib.urlencode({'q': q, 'h': nfetch,
                                          'f': nretrieved, 'format': 'xml'})
                print "Retrieving %s" % (API_URL + query)
                print "Writing results into %s" % data_dir
                urllib.urlretrieve(API_URL + query, data_dir)
                context = etree.iterparse(data_dir, events=('end',),
                                          tag=('hits'))

                with open(QRELS_DIR + "qrels_%d.txt" % topic_num, "a") as f:
                    res, nresults = parse(context)
                    if nretrieved == 0:  # first fetch
                        maxscore = res[min(10, len(res))-1]['score']
                        for d in res[:10]:  # process top10
                            f.write('%s\t0\t%s\t1\n' % (topic_num, d['key']))
                            if d['key'] not in results:
                                results.append(d['key'])
                        res = res[10:]
                    for d in res:  # process results past top10 with same score
                        if d['score'] < maxscore:
                            nretrieved = nresults
                            break
                        f.write('%s\t0\t%s\t1\n' % (topic_num, d['key']))
                        if d['key'] not in results:
                            results.append(d['key'])
                nretrieved += nfetch
    print "#Results: " + str(len(results))
    open(DBLP_RESULTS_DIR, 'w').close()
    with open(DBLP_RESULTS_DIR, "a") as rf:
        for res in results:
            rf.write('%s\n' % res)
