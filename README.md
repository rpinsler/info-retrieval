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

The easiest way to use the applications is to run `python run_app.py` and follow the instructions. If you want to call the functions directly (e.g. to build a UI on top), follow the steps below.

**Hint:** If you get a memory error, try to reduce the number of topics.

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
svy.write_to_file(path) # default: ./temp
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

Running `python run_app.py` shows the following dialogue, where we can enter our search query: 2015.

```
Search for most popular topics in a given year. Press enter with no input to continue.
Year: 2015
```

As a result, we get the top 10 most popular topics with the number of occurences in the paper titles shown in parentheses:

```
Results:
1) case study (1294)
2) wireless sensor networks (978)
3) performance analysis (525)
4) special issue (455)
5) performance evaluation (397)
6) cognitive radio networks (350)
7) comparative study (344)
8) empirical study (315)
9) neural network (313)
10) genetic algorithm (303)
```

#### Finding similar publication venues and year ####

Similarly, we can search for the most similar publication venues and years. Since we are using Latent Dirichlet Allocation (LDA), we first have to learn the model. The output should look similar to this:

```
Search for most similar publication venues and years. This requires to first run LDA (may take some minutes).
Do you want to continue? (y/n): y
Running LDA...
INFO:lda:n_documents: 52113
INFO:lda:vocab_size: 41704
INFO:lda:n_words: 22698646
INFO:lda:n_topics: 10
INFO:lda:n_iter: 100
INFO:lda:<0> log likelihood: -239102931
INFO:lda:<10> log likelihood: -200741256
...
INFO:lda:<99> log likelihood: -186544533

Finished LDA.
```

Afterwards, we can send our query, for example ICML 2008:

```
Search for most similar publication venues and years. Press enter with no input to continue.
Venue: ICML
Year: 2008

Results:
1) NIPS 2013 (0.9962)
2) NIPS 2014 (0.9961)
3) ICML 2013 (0.9956)
4) ICML 2006 (0.9954)
5) NIPS 2007 (0.9953)
6) NIPS 2010 (0.9953)
7) AISTATS 2012 (0.9946)
8) Journal of Machine Learning Research 2010 (0.9945)
9) ICML 2007 (0.9944)
10) ICML 2011 (0.9943)
```

which will output the top-10 most similar publication venues and years (except itself), with the topic similarity scores shown in parentheses.
