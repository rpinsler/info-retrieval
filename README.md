# info-retrieval

This is a basic search engine for the [dblp](http://dblp.uni-trier.de/) computer science bibliography with applications in Information Retrieval. It is built on top of [PyLucene](https://lucene.apache.org/pylucene/index.html), a python extension of the highly-popular full-text search engine [Lucene](https://lucene.apache.org/).

------------------

## Installation

The project has the following dependencies:
- PyLucene (see [installation instructions](http://lucene.apache.org/pylucene/install.html))
- lxml
- Flask

For the applications, more packages are required:
- nltk (run nltk.download() and install all packages)
- numpy
- scikit-learn

To set up the project, download the xml and dtd files of the [dblp dataset](http://dblp.uni-trier.de/xml/
) into the *data/* folder.

------------------

## Usage

You can use one of the following ways to interact with the search engine:
- **local web UI**: run `python web/ui.py` to start a local server. Open http://127.0.0.1:5000/ in your browser and start searching!
- **CLI**: run `python main.py` and follow the instructions.

------------------

## Examples

### Applications

#### Finding popular topics

Before running the program, building index is required.
```python
from index import Indexer

# building index for the application.
Indexer(DATA_DIR, INDEX_DIR, context, analyzer)
```
After building index, we can send query (a year), retrieve all the titles in the year and find the most popular topics in the year.
```python
from popular_topics import PopularTopics

# create an analyzer before using this application.
pt = PopularTopics(index_dir, analyzer)
results = pt.get_popular_topics(query_year, top_k)
```

#### Finding similar publication venues and years
For finding similar publication venues and years, there is no need to build index because all the titles in the dataset will be used.
If this is the first time you run this code, then you need to build a [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) model using
```python
from similar_venue_year import SimilarVenueYear
svy = SimilarVenueYear()
svy.lda_modeling(context, n_topics=10, n_iter=100)
```
You may want to store the model so the next time you can just load the model from files, instead running lda again.
```python
svy.write_to_file(path) # defalut: ./temp
svy.load_from_file(path)
```
Query for the top-k similar publication venues and years:
```python
results = svy.query_venue_year(venue='SIGIR', year='2015', top_k=10)
```