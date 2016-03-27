def search(self,query,adv_query,N):
  bq = BooleanQuery()
  if query != '':
    # handle phrases in standard search
    pq,query = extract_pq(query,'content')
    if pq is not None:
      bq.add(pq,BooleanClause.Occur.MUST)
  if query != '':
    # handle remaining keywords
    qparser = QueryParser(VERSION,'content',
      self.analyzer)
    q = qparser.parse(query)
    bq.add(q,BooleanClause.Occur.SHOULD)

  if adv_query is not None:
    for field,query in adv_query.iteritems():
      # handle phrases in advanced search
      pq,query = extract_pq(query,field)
      if pq is not None:
        bq.add(pq,BooleanClause.Occur.MUST)
      if query != '':
        # handle remaining keywords
        qparser = QueryParser(VERSION,field,
          self.analyzer)
        q = qparser.parse(query)
        bq.add(q,BooleanClause.Occur.MUST)
  return self.searcher.search(bq,N).scoreDocs
