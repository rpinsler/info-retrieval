INDEX_DIR = 'index'
DATA_DIR = 'data/dblp.xml'

config = {'lowercase':True,'stemming':True, 'stopwords':True}
title_analyzer = CustomAnalyzer(config)
per_field = HashMap()
per_field.put("title",title_analyzer)
default = StandardAnalyzer(VERSION)
analyzer = PerFieldAnalyzerWrapper(default,per_field)
Indexer(DATA_DIR,INDEX_DIR,analyzer)
