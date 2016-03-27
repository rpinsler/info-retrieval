def extract_pq(self,q,field,slop=0,boost=5):
  phrases = re.findall(r'"([^"]*)"',q)
  if len(phrases) == 0:
    return None,q

  q = re.sub(r'"([^"]*)"',"",q).strip()
  bq = BooleanQuery()
  for phrase in phrases:
    qparser = QueryParser(VERSION,field,self.analyzer)
    # handle phrase and single keywords
    pq = qparser.parse('%s "%s"~%d^%.1f' % (phrase,phrase,slop,boost))
    bq.add(pq,BooleanClause.Occur.MUST)
  return bq,q
