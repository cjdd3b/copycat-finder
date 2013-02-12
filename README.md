Copycat Finder
==============

This project identifies model legislation and other copycat bills that appear in multiple state legislatures.

In its current form, the code is designed mainly to prove that pairwise text comparison is possible at sufficient scale to compare all state legislation at once. As such, the analysis here **only deals with bill titles, not full bill text**. The main reason for that is practical: Sunlight's [http://openstates.org/](OpenStates project), the data source for this project, does not collect full bill text. Scraping and cleaning bill text from 50 states is another can of worms. Still, the methods used here for comparing bill titles should be able to apply to full bill text with little to no modification.

## The method

Pairwise document comparison at scale is a tricky problem. Executed naively (using loops to compare every document against every other document), even a 100,000-record document set could require literally 10 billion individual comparisons -- way too many for a single computer to handle in any reasonable amount of time. On the flip side, a less naive computation using linear algebra to generate a [similarity matrix](http://en.wikipedia.org/wiki/Similarity_matrix) can end up consuming an equally preposterous amount of RAM.

My early attempts to solve this problem relied on raw computing muscle, using a number of servers running a parallel [map-reduce workflow](https://github.com/cjdd3b/pairwise-mapreduce) developed by researchers at the University of Maryland. That worked fine, but it was inelegant, costly and difficult to spin up.

The approach used in this project fixes those problems by using a three-step workflow that can execute millions of comparisons in reasonable time on an individual laptop. After preprocessing, the workflow first uses [k-means clustering](http://en.wikipedia.org/wiki/K-means_clustering) to break the problem into smaller subproblems, then relies on Python's [Gensim](http://radimrehurek.com/gensim/) library to construct large similarity matrices using disk space rather than RAM. Finally, the cosine distance bewtween the tf-idf vectors of title pairs is used to determine similarity, with all groups of bills having similarity in excess of a given threshold being linked together.

Processing the attached dataset of almost 400,000 bill titles takes about an hour on a Macbook Air. More detail on each step follows:

### Initial clustering

As I learned while working on the [fec-standardizer](https://github.com/cjdd3b/fec-standardizer) project, it helps when doing large-scale text comparison to break large datasets into smaller clusters, which can each be processed separately by a given workflow. This step alone can reduce the complexity (and running time) of your process by several orders of magnitude, while also allowing the workflow to be spread over multiple processors or machines if necessary.

In this project, the initial splits are done using a variant of k-means clustering known as [mini-batch k-means](http://www.eecs.tufts.edu/~dsculley/papers/fastkmeans.pdf). Mini-batch k-means runs much, much faster than traditional k-means, at the cost of a little precision. But because we're just trying to cut our documents into a handful of rough chunks, precision isn't especially important here. The particular implementation of the algorithm used here comes from [scikit-learn](http://scikit-learn.org/dev/modules/generated/sklearn.cluster.MiniBatchKMeans.html).

I tried several different numbers of clusters for the processing step but ultimately settled on 25. No particular reason -- it just seemed small enough not to overfit, while keeping groups to a size my laptop could handle. As you'll see later, this is one of the steps that could be refined to improve the overall workflow.

### Disk storage vs. RAM

Once the initial document set is split into clusters, the program then constructs pairwise similarity matrix from each cluster one at a time. That said, some of the groups that k-means returns still contain upwards of 100,000 documents, so those similarity matrices are still pretty big.

That's where [Gensim](http://radimrehurek.com/gensim/) comes in. Among many other useful things, Gensim is ingeniously structured to shard large similarity matrices to the hard disk rather than trying to store them in memory. It comes at the cost of speed, but it enables brute force pairwise comparisons without resorting to clever algorithmic tricks or heuristics that might make for less precise comparisons.

### The comparisons themselves

The comparisons themselves aren't based on anything especially interesting. Bills are compared in a standard way using [cosine similarity](http://en.wikipedia.org/wiki/Cosine_similarity) between their [tf-idf](http://en.wikipedia.org/wiki/Tf%E2%80%93idf) vectors, yielding a score between -1 and 1. In this example, two documents with a similarity of at least 0.7 are considered similar, although that number could easily be adjusted to be more or less permissive.

## The results

FASCINATING LOOK AT THE MODERN STATE OF FEDERALISM AND INTRASTATE LAWMAKING

### Specific examples

Even this cursory and incomplete analysis revealed hundreds of apparent model bills crafted by business and ideological groups, as well as providing a fascinating look into how lawmaking trends evolve and move between the states. Based on a very quick read of the results, here are a few interesting finds:

**ALEC bills**: An ALEC bill known as the [Successor Corporation Asbestos-Related Liability Act](http://www.alecexposed.org/w/images/9/9a/0E2-Successor_Asbestos-Related_Liability_Fairness_Act_Exposed.pdf) was introduced in at least six states (and probably more) between 2009 and 2012. Among many other ALEC bills, legislation such as the [Transparency in Lawsuits Protection Act](http://www.alec.org/initiatives/expanding-the-law-under-the-new-restatement-of-torts/transparency-in-the-creation-of-new-ways-to-sue/), the [Family Education Tax Credit Program Act](http://alecexposed.org/w/images/7/77/2D9-THE_FAMILY_EDUCATION_TAX_CREDIT_PROGRAM_ACT_Exposed.pdf); and a [resolution](http://www.alecexposed.org/w/images/9/9d/8B17-The_Balanced_Budget_Amendment_Resolution_exposed.pdf) encouraging Congress to pass a balanced budget were also proposed in multiple states during that time (apologies for all those links to ALEC Exposed). Other uniform legislation, such as bills proposed by the BLAH.

**Other interest group bills**: The dataset contains hundreds of bills introduced in multiple states that clearly originated from or have been supported by national interest groups. Among them are bills that expand grandparents' rights to child visitation (supported by the AARP; introduced in at least X states); the Pain-Capable Unborn Children Act (supported by pro-life groups; introduced in at least 7 states); bills requiring the disclosure of fluids used in hydraulic fracturing (supported by X; introduced in at least 10 states); bills that loosen rules related to direct wine shipping (supported by the beverage industry; introduced in at least X states); AND BLAH.

**Signs of the times**: Motor vehicle fuel theft. AZ SB1070 in at least three other states. Medical marijuana

**Grandparent visitation**: The AARP was behind a push in at least six states to extend grandparents' rights to child visitation. **Phosphorous in detergent**: A number of states in 2011 proposed nearly identical laws that required detergent manufacturers to reformulate their product to reduce or eliminate phosphates. The bills were pushed by BLAH and appear to related to the trend described in [this NYT story](http://www.nytimes.com/2010/09/19/science/earth/19clean.html) from 2010. Medical marijuana act

**Benign but interesting bills**: Even completely benign bills, like one that designates a day in honor of the Alpha Kappa Alpha sorority, reveal the breadth of influence that some organizations enjoy. This particular sorority was honored in at least eight states between 2009 and 2012. Other examples include resolutions condemning various diseases, such as lupus, heart disease, breast cancer and others that are often supported by powerful groups like the Susan G. Koman foundation. Bills designed to make a political statement, such as a popular one honoring Ronald Reagan, can also show solidarity or division between partisans across multiple states. Many of these bills demonstrate a level of centralized coordination and government relations strategy that highlights how intrastate laws garner momentum and support.

## Next steps

As I said above, these early efforts are admittedly rough and are meant only to demonstrate the viability of this technique and the journalistic potential of its results.

All in all, I'm satisfied that the method outlined here is effective, but it still needs to be refined. Some simple and obvious next steps might include processing text to cut out things like non-alphanumeric characters; adjusting the document similarity score to see how it affects results; and optimizing the number of clusters for k-means, using techniques such as the [Elbow Method](http://en.wikipedia.org/wiki/Determining_the_number_of_clusters_in_a_data_set) to ensure bills are clustered properly. 

Beyond that, I would love to extend the analysis beyond bill titles to the full text of the legislation itself. Looking only at bill titles makes it possible to find some legislative trends, but ideally the approach would be much more granular -- looking at complete bill text tokenized into sections or even sentences. Not only would that approach reveal model legislation that might not be identified by titles alone, but it could also reveal common language inserted into completely different bills, possibly crafted by lobbyists and disseminated across multiple states.

The clustering and processing method demonstrated here could easily be extended to the millions or even tens of millions of individual text elements necessary to do sentence-level similarity checks. Mini-batch k-means should have no problem quickly separating those text tokens into clusters (perhaps with the help of a large or extra large EC2 instance), which could then be processed in parallel across multiple EC2 instances.

That of course still leaves open a big question: What's the best way to obtain full bill text? OpenStates only provides bill URLs, which would still require someone to write parsers to process the unique bill format of each of the 50 states -- a task that would be time-consuming but not necessarily difficult. I've included a sample of how this might work in the parsers directory of this repository.

Another option would be working with a company like [Legiscan](http://legiscan.com/), which archives full bill text at the state and federal levels. They appear willing to structure [custom API access deals](http://legiscan.com/features) on request. It might also be possible to acquire the necessary text through their free API tier. Either way, it's worth further exploration if this project moves forward.