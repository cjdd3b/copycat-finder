Copycat Finder
==============

This project identifies model legislation and other copycat bills that appear in multiple state legislatures.

In its current form, the code is designed mainly to prove that pairwise text comparison is possible at sufficient scale to compare all state legislation at once. As such, the analysis here **only deals with bill titles, not full bill text**. The main reason for that is practical: Sunlight's [http://openstates.org/](OpenStates project), the data source for this project, does not collect full bill text. Scraping and cleaning bill text from 50 states is another can of worms (and one that is addressed briefly in the code here). But the methods used here for comparing bill titles should be able to apply to full bill text with little to no modification.

## The method

Pairwise document comparison at scale is a tricky problem. Executed naively (using loops to compare every document against every other document), even a 100,000-record document set could require literally 10 billion individual comparisons -- way too many for a small laptop to handle in any reasonable amount of time. On the flip side, a less naive computation using linear algebra to generate a [similarity matrix](http://en.wikipedia.org/wiki/Similarity_matrix) can end up consuming an equally preposterous amount of RAM.

My early attempts to solve this problem relied on raw computing muscle, using a number of servers running a [map-reduce workflow](https://github.com/cjdd3b/pairwise-mapreduce) developed by researchers at the University of Maryland. That worked fine, but it was inelegant, costly and difficult to spin up.

The approach used in this project fix those problems by using a three-step workflow that executes in reasonable time on an individual laptop. After preprocessing, the workflow first uses K-Means clustering to break the problem into smaller subproblems, then relies on Python's [Gensim](http://radimrehurek.com/gensim/) library to construct large similarity matrices using disk space rather than RAM. Finally, the cosine distance of each title's tf-idf vector is used to determine similarity, with all groups of bills having similarity in excess of a given threshold being linked together.

Processing the attached dataset of almost 400,000 bill titles takes between 1 and 2 hours on a Macbook Air. More detail on each step follows:

### Initial clustering

As I learned while working on the [fec-standardizer](https://github.com/cjdd3b/fec-standardizer) project, it helps when doing large-scale text comparison to break the whole dataset you want to compare into smaller clusters, which can each be processed by your workflow separately. This step alone can reduce the complexity (and running time) of your process by several orders of magnitude, while also allowing the workflow to be spread over multiple processors or machines if necessary.

In this project, the initial splits are done using a variant of [k-means clustering](http://en.wikipedia.org/wiki/K-means_clustering) known as [mini-batch k-means](http://www.eecs.tufts.edu/~dsculley/papers/fastkmeans.pdf). Mini-batch k-means runs much, much faster than traditional k-means, at the cost of a little precision. But because we're just trying to cut our documents into a handful of rough chunks, precision isn't especially important. The particular implementation of the algorithm used here comes from [scikit-learn](http://scikit-learn.org/dev/modules/generated/sklearn.cluster.MiniBatchKMeans.html).

I tried several different numbers of clusters for the processing step but ultimately settled on 25. No particular reason -- it just seemed small enough not to overfit, while keeping groups to a size my laptop could handle.

### Disk storage vs. RAM

Once the initial document set is split into 25 clusters, the clustering program then loops through each of those clusters and creates a pairwise similarity matrix from it. Problem is, some of the groups that k-means returns still contain upwards of 100,000 documents, so those similarity matrices are still pretty big.

That's where [Gensim](http://radimrehurek.com/gensim/) comes in. Among many other useful things, Gensim is ingeniously structured to shard large similarity matrices to to the hard disk rather than trying to store them in memory. It comes at the cost of speed, but it enables brute force pairwise comparisons without resorting to clever algorithmic tricks or heuristics that might make the matching process less precise. It makes for a more complete scan, which benefits us in our search for potential copycat bills.

### The comparisons themselves

The comparisons themselves don't do anything especially interesting. Bills are compared in a standard way using [cosine similarity](http://en.wikipedia.org/wiki/Cosine_similarity) between their [tf-idf](http://en.wikipedia.org/wiki/Tf%E2%80%93idf) vectors, yielding a score between -1 and 1. In this example, two documents with a similarity of at least 0.7 are considered matches, although that number could easily be adjusted to be more or less permissive.

## The results

### Specific examples

## Next steps

As I said above, these early efforts are admittedly rough and are meant primarily to demonstrate the viability of this technique and the journalistic potential of its results.

The next most obvious step is to clean up the bill text input, cutting out things like non-alphanumeric characters. At this point, I've mostly disregarded that cleanup out of laziness. Further tests, such as the [Elbow Method](http://en.wikipedia.org/wiki/Determining_the_number_of_clusters_in_a_data_set), should also be run to determine the optimal number of clusters for k-means.

Beyond that, the next step would be to extend the analysis beyond bill titles to the bill text itself. Looking only at bill titles makes it possible to find some model legislation, but ideally the approach would be much more granular -- looking at bill text tokenized into sections or even sentences. Not only would that approach reveal model legislation that might otherwise not be picked up by titles alone, but it could also reveal common language inserted into completely different bills, possibly crafted by lobbyists and disseminated in multiple states.

The clustering and processing method demonstrated here could easily be extended to the millions or even tens of millions of individual text elements necessary to do sentence-level similarity checks. Mini-batch k-means should have no problem quickly separating those text tokens into clusters (perhaps with the help of a large or extra large EC2 server), which could then be processed in parallel across multiple EC2 instances.

That of course still leaves the most significant time investment: scraping the bill text from 50 states. OpenStates provides bill URLs, which gives us a huge head start. The only remaining task would be writing parsers to extract clean text from each state's unique bill format -- something that would be time-consuming but not necessarily difficult. I've included some code in the repository's **parsers** folder that shows how that process might be started.