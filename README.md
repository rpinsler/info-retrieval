# info-retrieval #

This is a basic search engine for the [dblp](http://dblp.uni-trier.de/) computer science bibliography with applications in Information Retrieval. It is built on top of [PyLucene](https://lucene.apache.org/pylucene/index.html), a python extension of the highly-popular full-text search engine [Lucene](https://lucene.apache.org/).

------------------

## Installation ##

The project runs on Python 2.7. 

The search engine has the following Python dependencies:
- PyLucene (see [installation instructions](http://lucene.apache.org/pylucene/install.html))
- lxml
- Flask

To run the applications, more packages are required:
- nltk (run `nltk.download()` and install all packages)
- numpy
- scikit-learn
- lda

If not specified otherwise, [pip](https://pip.pypa.io/en/stable/quickstart/) can be used to install the packages, i.e. use `pip install <package>`.

To set up the project, download the xml and dtd files of the [dblp dataset](http://dblp.uni-trier.de/xml/
) into the *data/* folder. You may also want to have a look into the *config.json* file, where some parameters can be set (e.g. the maximum number of results that are returned from the search).

------------------

## Usage ##

Make sure you execute all commands from within the program directory: `cd info-retrieval`.
As a first step, you should run `python build_index.py` to parse the DBLP dataset and construct a Lucene index from it. The output should look similar to this:
```
100000 documents processed...
200000 documents processed...
...
3200000 documents processed...
Finished indexing. 3205115 documents indexed in total.

```

### Search Engine ###

You can use one of the following ways to interact with the search engine:
- **local web UI**: run `python ui_search.py` to start a local server. Open http://127.0.0.1:5000/ in your browser and start searching!
- **CLI**: run `python cli_search.py` and follow the instructions.

### Applications ###

#### Finding popular topics ####
By sending a query (i.e. a year), the application can retrieve all titles from the paper published in that year and find the most popular topics.
```python
from popular_topics import PopularTopics

# create an analyzer before using this application.
pt = PopularTopics(index_dir, analyzer)
results = pt.get_popular_topics(query_year, top_k)
```

#### Finding similar publication venues and years ####
We use [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) to find the most similar publication venues and years. If this is the first time you run this code, then you need to build an LDA model using:
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

------------------

## Examples ##

### Search Engine ###

Let's use the command-line interface (`python cli_search.py`) to search for the phrase "query optimization":
```
Standard search. Type ':q' to quit.
Query: "query optimization"
```
However, we also want to restrict the results to publications from 2000. This is where the advanced search comes into play:
```
Use advanced search? (y/n): y
Advanced search. Hit enter with no input to skip field.
Title: 
Authors: 
Year: 2000
Venue: 
```
This yields the following result:
```
Execute search.
Searching for: "query optimization"
Searching for (advanced):  {'venue': '', 'authors': '', 'year': '2000', 'title': ''}
Detected phrases:  ['query optimization']
Lucene query: +(+(content:query content:optimization content:"query optimization"^5.0)) +year:2000
1257 results found (0.20s)
Showing only top 10

Result list:
1) conf/edbt/Josinski00 (relevance: 3.58)
Dynamic Query Optimization and Query Processing in Multidatabase Systems
Henryk Josinski
EDBT PhD Workshop - 2000
2) journals/is/PlodzienK00 (relevance: 3.51)
Object Query Optimization through Detecting Independent Subqueries
Jacek Plodzien, Anna Kraken
Inf. Syst. - 2000
3) journals/dr/Sellis00c (relevance: 3.51)
Review - Query Optimization by Simulated Annealing
Timos K. Sellis
ACM SIGMOD Digital Review - 2000
4) journals/dr/Srivastava00a (relevance: 3.51)
Review - Query Optimization by Predicate Move-Around
Divesh Srivastava
ACM SIGMOD Digital Review - 2000
5) journals/dr/Wu00 (relevance: 3.51)
Review - Query Optimization for XML
Yuqing Melanie Wu
ACM SIGMOD Digital Review - 2000
6) conf/sac/HaratyF00 (relevance: 3.51)
Distributed Query Optimization Using PERF Joins
Ramzi A. Haraty, Roula C. Fany
SAC (1) - 2000
7) conf/cata/HaratyF00 (relevance: 3.51)
A PERF solution for distributed query optimization
Ramzi A. Haraty, Roula C. Fany
Computers and Their Applications - 2000
8) conf/edbt/Wang00 (relevance: 3.51)
Cost-Based Object Query Optimization
Quan Wang
EDBT PhD Workshop - 2000
9) conf/sbbd/AndradeS00 (relevance: 3.51)
Query Optimization in KESS - An Ontology-Based KBMS
Henrique Andrade, Joel H. Saltz
SBBD - 2000
10) conf/iceis/OommenR00 (relevance: 3.51)
An Empirical Comparison of Histogram-Like Techniques for Query Optimization
B. John Oommen, Luis Rueda
ICEIS - 2000
```

Looks not too bad, right? However, you may have noticed that some of the outputs are rather verbose from an end-user perspective (e.g. the internal Lucene query). This is because the command-line interface is meant to be used for debugging purposes. For example, the output shows that the search has found a total of 1257 hits, which seems to be quite a lot. By looking at the internal Lucene query, we can conclude that this is because we also accept results that contain either the term *query* or *optimization*. This considerably increases recall at the cost of some more false positives. If that is not desired, we could go back to the source code and adapt this aspect to our needs. 

In reality, an end user would prefer to use the web UI, which is mostly self-explanatory (advanced query input not shown):
![Search results for query "query optimization" year:2000](https://github.com/rpinsler/info-retrieval/blob/master/report/img/search.png)

### Applications ###

#### Finding popular ####

The result is like:

```
2015
case study 1294
wireless sensor networks 978
performance analysis 525
special issue 455
performance evaluation 397
cognitive radio networks 350
comparative study 344
empirical study 315
neural network 313
genetic algorithm 303
```

The first line is the query year, and the remainings are the top 10 most popular topics, with the frequency of appearing in the paper titles in the query year.

#### Finding similar publication venues and year ####

The result is like:

```
Query: ICML 2008

NIPS 2013 0.996201855584
NIPS 2014 0.996095504679
ICML (3) 2013 0.99563417354
ICML 2006 0.995400670197
NIPS 2007 0.995344881108
NIPS 2010 0.995275601664
AISTATS 2012 0.994550320804
Journal of Machine Learning Research 2010 0.994530348355
ICML 2007 0.994376385049
ICML 2011 0.994253713082
```

The first line is the query venue and year, and the remainings are the top 10 most similar publication venues and years (except itself), with the topic similarities of appearing in the paper titles in the query year.