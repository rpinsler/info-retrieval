# info-retrieval

This is a basic search engine for the [dblp](http://dblp.uni-trier.de/) computer science bibliography with applications in Information Retrieval. It is built on top of [PyLucene](https://lucene.apache.org/pylucene/index.html), a python extension of the highly-popular full-text search engine [Lucene](https://lucene.apache.org/).

------------------

## Installation

The project has the following dependencies:
- PyLucene (see [installation instructions](http://lucene.apache.org/pylucene/install.html))
- lxml
- Flask

For the applications, more packages are required:
- nltk
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
