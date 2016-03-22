from lxml import etree
import urllib

RECORD_TYPES = ["Conference and Workshop Papers", "Journal Articles"]


def parse(context, f, topic_num):
    """
    http://lxml.de/parsing.html#modifying-the-tree
    Based on Liza Daly's fast_iter
    http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    See also http://effbot.org/zone/element-iterparse.htm
    """
    for event, elem in context:
        self.parse_element(elem, f, topic_num)
        # It's safe to call clear() here because no descendants will be
        # accessed
        elem.clear()
        # Also eliminate now-empty references from the root node to elem
        for ancestor in elem.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
    del context


def parse_element(elem, f, topic_num):
    try:
        for ch in elem:
            key = None
            if ch.tag == 'type' and ch.text not in RECORD_TYPES:
                return
            elif ch.tag == 'url':
                key = ch.text[20:]

        f.write('%s\t0%s\t1\n' % (topic_num, key))

    except Exception, e:
        print "Parse error:", e


if __name__ == "__main__":
    tree = etree.parse("eval/topics")
    for element in tree.iter():
        if element.tag == 'num':
            topic_num = int(element.text)
        elif element.tag == 'query':
            data_dir = 'eval/qrels_dblp/q_%d' % topic_num
            api_url = "http://dblp.uni-trier.de/search/publ/api?"
            query = urllib.urlencode({'q': element.text, 'h': 1000,
                                      'format': 'xml'})
            print "Retrieving %s" % (api_url + query)
            print "Writing results into %s" % data_dir
            urllib.urlretrieve(api_url + query, data_dir)
            context = etree.iterparse(data_dir, events=('end',),
                                      tag=('hit'))

            open("eval/qrels_dblp/qrels_%d" % topic_num, 'w').close()
            with open("eval/qrels_dblp/qrels_%d" % topic_num, "a") as f:
                parse(context, topic_num, f)
