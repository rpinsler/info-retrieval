from lxml import etree


def parse_element(elem):
    # index at least the following attributes:
    # - paper id (or key)
    # - paper title
    # - authors
    # - year of publication
    # - publication venue: journal for article, booktitle for inproceedings

    entry = {'id': elem.get("key")}
    for ch in elem:
        if ch.tag == 'title':
            entry['title'] = ch.text
        elif ch.tag == 'author':
            entry.setdefault('authors', []).append(ch.text)
        elif ch.tag == 'year':
            entry['year'] = ch.text
        elif ch.tag == 'journal' or ch.tag == 'booktitle':
            entry['venue'] = ch.text
    print(entry)

    # do actual indexing on the entry


def parse(context, func, *args, **kwargs):
    """
    http://lxml.de/parsing.html#modifying-the-tree
    Based on Liza Daly's fast_iter
    http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    See also http://effbot.org/zone/element-iterparse.htm
    """
    for event, elem in context:
        func(elem, *args, **kwargs)
        # It's safe to call clear() here because no descendants will be
        # accessed
        elem.clear()
        # Also eliminate now-empty references from the root node to elem
        for ancestor in elem.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
    del context

if __name__ == "__main__":
    data_fp = "data/dblp.xml"
    context = etree.iterparse(data_fp, events=('end',),
                              tag=('article', 'inproceedings'),
                              dtd_validation=True)
    parse(context, parse_element)
