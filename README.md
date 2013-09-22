Copycat Finder
==============

This project is a simple approach for finding pieces of legislation that appear in multiple state legislatures.

For now, the analysis here **only deals with bill titles, not full bill text**. Sunlight's [OpenStates project](http://openstates.org/), the data source for this project, does not index full bill text. Scraping and cleaning bill text from 50 states is another can of worms. Still, the methods used here for comparing bill titles should be able to apply to full bill text with minor modifications.

## Running the app

The app is written in Python and uses Django for some database help behind the scenes. Running the app should be pretty straightforward.

First, in either your global Python environment or a self-contained virtual environment, install the requirements by typing ```pip install -r ./requirements.txt```.

Next, you'll need to set up a fresh SQLite database, which you can do by typing ```python manage.py syncdb``` and following the instructions.

Then you'll need to fill your database with bill titles from OpenStates. The code for doing that is in copycat/bin/importer.py. If you simply run that script with ```python importer.py```, your database should populate automatically with bills from 39 state legislatures' 2013 session (get some coffee -- it takes a while).

Finally, running the analysis itself is as simple as running ```python cluster.py```, which is located in the same directory as the importer. That script will output a graphml file in copycat/bin/output/, which you can open and explore using software like [Gephi](http://www.gephi.org). Nodes that are connected together in the graph represent similar bills.

## A few other notes

There are a lot of methods available for grouping similar documents together, including more efficient approaches such as [locality-sensitive hashing](http://en.wikipedia.org/wiki/Locality-sensitive_hashing). The method here is designed to have simple intuition while still being relatively efficient.

The approach relies on building a [similarity matrix](http://en.wikipedia.org/wiki/Similarity_matrix) that shows how similar every document in each cluster is to each other. In a sufficiently large dataset, that matrix can take up a large amount of RAM, which is why the workflow also relies on help from a Python library called [Gensim](http://radimrehurek.com/gensim/), which shards large matrices to disk rather than storing them in memory.

The process also uses a clustering algorithm called mini-batch k-means clustering, which runs more quickly than conventional k-means but at the expense of a little precision. For some intuition on how the conventional k-means algorithm works, I put together a [documented version](https://github.com/cjdd3b/car-datascience-toolkit/blob/master/cluster/kmeans.py) you can read though.

## Contact

I'm at chase.davis@gmail.com if you have any questions. Thanks!