VERSION = Version.LUCENE_CURRENT
class CustomAnalyzer(PythonAnalyzer):
  def __init__(self,config):
    self.lowercase = config['lowercase']
    self.stemming = config['stemming']
    self.stopwords = config['stopwords']
    PythonAnalyzer.__init__(self)

  def createComponents(self,fieldName,reader):
    src = StandardTokenizer(VERSION,reader)
    fltr = StandardFilter(VERSION,src)
    if self.lowercase:
      fltr = LowerCaseFilter(VERSION,fltr)
    if self.stemming:
      fltr = PorterStemFilter(fltr)
    if self.stopwords:
      sw = StopAnalyzer.ENGLISH_STOP_WORDS_SET
      fltr = StopFilter(VERSION,fltr,sw)
    return self.TokenStreamComponents(src,fltr)
