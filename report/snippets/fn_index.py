FIELDS = ['title','author','year','journal','booktitle']
HTML_TAGS = ('i','ref','sub','sup','tt')

def index_document(self,elem):
  etree.strip_tags(elem,HTML_TAGS)
  doc = Document()
  f = StringField('id',elem['key'],Store.YES)
  doc.add(f)
  for ch in elem:
    if ch.tag not in FIELDS:
      continue
    if ch.text is None:
      ch = etree.tostring(ch)
      ch = self.htmlparser.unescape(ch)
      ch = etree.fromstring(ch)

    if ch.tag == 'title':
      f = TextField('title',ch.text,Store.YES)
    elif ch.tag == 'author':
      f = TextField('authors',ch.text,Store.YES)
    elif ch.tag == 'year':
      f = StringField('year',ch.text,Store.YES)
    else:
      f = TextField('venue',ch.text,Store.YES)

    doc.add(f)
    cf = TextField('content',ch.text,Store.NO)
    doc.add(cf)
  self.writer.addDocument(doc)
