VERSION = Version.LUCENE_CURRENT
def search(query,adv_query,N,analyzer,searcher):
  bq = BooleanQuery()
  if query != '':
    # handle phrases in standard search
    pq,query = get_pq(query,'content')
    if pq is not None:
        bq.add(pq,BooleanClause.Occur.MUST)

  if query != '':
    # handle remaining keywords
    qparser = QueryParser(VERSION,
                          'content',
                          analyzer)
    q = qparser.parse(query)
    bq.add(q,BooleanClause.Occur.SHOULD)

  if adv_query is not None:
    for field,query in adv_query.iteritems():
      # handle phrases in advanced search
      pq,query = get_pq(query,field)
      if pq is not None:
        bq.add(pq,BooleanClause.Occur.MUST)
      if query != '':
        # handle remaining keywords
        qparser = QueryParser(VERSION,
                              field,
                              analyzer)
        q = qparser.parse(query)
        bq.add(q,BooleanClause.Occur.MUST)

  start = time.clock()
  docs = searcher.search(bq,N).scoreDocs
  end = time.clock()
  duration = end-start
  return docs,duration

def get_pq(q,field,analyzer,slop=0,boost=5):
  phrases = re.findall(r'"([^"]*)"',q)
  if len(phrases) == 0:
    return None,q

  q = re.sub(r'"([^"]*)"',"",q).strip()
  bq = BooleanQuery()
  for phrase in phrases:
    qparser = QueryParser(VERSION,
                          field,
                          analyzer)
    # handle phrase and single keywords
    pq = qparser.parse('%s "%s"~%d^%.1f' %
                       (phrase,phrase,
                        slop,boost))
    bq.add(pq,BooleanClause.Occur.MUST)
  return bq,q
