class Searcher():
  def __init__(self,index_dir,analyzer):
    directory = SimpleFSDirectory(File(index_dir))
    reader = DirectoryReader.open(directory)
    self.searcher = IndexSearcher(reader)
    self.analyzer = analyzer

  def search(self,query,adv_query,N=0):
    # perform search for given query

  def extract_pq(self,q,field,slop=0,boost=5):
    # extract phrases from given query
