# info-retrieval #

This is a basic search engine for the [dblp](http://dblp.uni-trier.de/) computer science bibliography with applications in Information Retrieval. It is built on top of [PyLucene](https://lucene.apache.org/pylucene/index.html), a python extension of the highly-popular full-text search engine [Lucene](https://lucene.apache.org/).

------------------

## Installation ##

The search engine has the following dependencies:
- PyLucene (see [installation instructions](http://lucene.apache.org/pylucene/install.html))
- lxml
- Flask

To run the applications, more packages are required:
- nltk (run `nltk.download()` and install all packages)
- numpy
- scikit-learn

If not specified otherwise, [pip](https://pip.pypa.io/en/stable/quickstart/) can be used to install the packages, i.e. use `pip install <package>`.

To set up the project, download the xml and dtd files of the [dblp dataset](http://dblp.uni-trier.de/xml/
) into the *data/* folder.

You may also want to have a look into the *config.json* file, where some parameters can be set.

------------------

## Usage ##

Make sure you execute all commands from within the program directory: `cd info-retrieval`

First, run `python build_index.py` to parse the DBLP dataset and construct a Lucene index from it.

Afterwards, you can use one of the following ways to interact with the search engine:
- **local web UI**: run `python ui_search.py` to start a local server. Open http://127.0.0.1:5000/ in your browser and start searching!
- **CLI**: run `python cli_search.py` and follow the instructions.

------------------

## Examples ##

Prerequisites: Make sure to construct an index of the dataset first: `python build_index.py`

### Applications ###

#### Finding popular topics ####

By sending a query (i.e. a year), the application can retrieve all titles from publications of that year and find the most popular topics.
```python
from popular_topics import PopularTopics

# create an analyzer before using this application.
pt = PopularTopics(index_dir, analyzer)
results = pt.get_popular_topics(query_year, top_k)
```

#### Finding similar publication venues and years ####
We will use [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) to find the most similar publication venues and years. If this is the first time you run this code, then you need to build an LDA model using:
```python
from similar_venue_year import SimilarVenueYear
svy = SimilarVenueYear()
svy.lda_modeling(context, n_topics=10, n_iter=100)
```
You may want to store the model so the next time you can just load the model from files, instead of running LDA again.
```python
svy.write_to_file(path) # defalut: ./temp
svy.load_from_file(path)
```
Query for the top-k similar publication venues and years:
```python
results = svy.query_venue_year(venue='SIGIR', year='2015', top_k=10)
```
