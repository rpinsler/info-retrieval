import urllib
import lxml


def check_config(config):
    """
    Checks configuration file and resets values to defaults, if necessary.
    """

    config = convert_keys_to_string(config)
    config['topN'] = check_config_entry(config, 'topN', int, 10)
    config['titleAnalyzer'] = check_config_entry(config, 'titleAnalyzer',
                                                 dict, {'lowercase': True,
                                                        'stemming': True,
                                                        'stopwords': True})
    return config


def check_config_entry(config, key, typeof, default):
    """
    Checks single config entry and resets value to default, if necessary.
    """
    if key in config:
        if isinstance(config[key], typeof):
            return config[key]
        else:
            print("Invalid configuration value for %s. " % key +
                  "Set to %s (default)." % default)
            return default

    else:
        return default


def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v))
                for k, v in dictionary.items())


def retrieve_snippet(self, docurl):
    """
    Scrapes abstract from given url by trying out some heuristics.
    However, there are performance issues as well as access
    restrictions from publisher side.
    """
    if docurl is None:
        return None

    # fetch website content
    # this can include multiple redirects, which makes it quite slow
    response = urllib.urlopen(docurl)
    doc = lxml.html.parse(response).getroot()

    # assume abstract is child <p> element from some container,
    # which has id or class abstract/Abstract
    abstract = doc.find_class('abstract')
    if len(abstract) == 0:
        abstract = doc.find_class('Abstract')
    else:
        abstract = abstract[0]
    if len(abstract) == 0:
        abstract = doc.get_element_by_id("abstract", None)
    else:
        abstract = abstract[0]
    if abstract is None:
        abstract = doc.get_element_by_id("Abstract", None)

    # if we were unsuccessful before, simply look for largest <p>
    # element on the website
    if abstract is None:
        elements = doc.xpath("//p")
        if len(elements) == 0:
            return None
        lens = [len(elem.text) if elem.text is not None else 0
                for elem in elements]
        if len(lens) == 0:
            return None
        abstract = [elements[lens.index(max(lens))]]

    for elem in abstract:
        # only return text if element has some minimum length
        if elem.tag == 'p' and len(elem.text) > 150:
            # shorten text if it's too long (which is mostly the case)
            # just take first 200 characters then
            if len(elem.text) > 200:
                return elem.text[:200] + "..."
            else:
                return elem.text
    return None
