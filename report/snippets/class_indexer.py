TAGS = ('article', 'inproceedings')
VERSION = Version.LUCENE_CURRENT
CREATE = IndexWriterConfig.OpenMode.CREATE

class Indexer():
  def __init__(self,data_dir,store_dir,analyzer):
    store = SimpleFSDirectory(File(store_dir))
    config = IndexWriterConfig(VERSION,analyzer)
    config.setOpenMode(CREATE)
    self.writer = IndexWriter(store,config)
    self.htmlparser = HTMLParser()
    self.index(data_dir)
    self.writer.close()

  def index(self,data_dir):
    context = etree.iterparse(data_dir,tag=TAGS,
      events=('end',),dtd_validation=True)
    for event,elem in context:
      self.index_document(elem)

    def index_document(self,elem):
      # indexes extracted element
