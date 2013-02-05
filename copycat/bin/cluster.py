import numpy, heapq, itertools
import networkx as nx
from gensim import similarities, corpora, models
from gensim.similarities.docsim import Similarity
from apps.bills.models import Bill

########## CLASSES ##########

class BillCorpus(object):
    def __init__(self, texts, dict):
        self.texts = texts
        self.dict = dict

    def __iter__(self):
        for line in self.texts:
            yield self.dict.doc2bow(line.lower().split())

########## MAIN ##########

if __name__ == '__main__':
    # First obtain documents to test
    bills = Bill.objects.all()[20000:30000]
    documents = bills.values_list('title', flat=True)

    # Load into gensim dictionary object
    dictionary = corpora.Dictionary(line.lower().split() for line in documents)

    # Filtering, stopword removal and other cleaning happens here. In this case, we're only
    # removing words that occur just once, but there's a lot more that could be done.
    #once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
    #dictionary.filter_tokens(once_ids)

    # Compact dictionary
    dictionary.compactify()

    # Now create corpus and tfidf model
    bc = BillCorpus(documents, dictionary)
    tfidf = models.TfidfModel(bc)

    G = nx.Graph() # Prep the networkX graph for later

    #Create and iterate over the similarity matrix
    index = Similarity(corpus=tfidf[bc], num_features=tfidf.num_nnz, output_prefix="shard")
    for i in enumerate(index):
        # Get the ids of values in each row that have cosine similarity > 0.7
        for j in numpy.nonzero(i[1] > 0.7)[0]:
            b1, b2 = bills[i[0]], bills[j]
            if b1.state <> b2.state:
                G.add_edge(b1.title, b2.title)

    nx.write_graphml(G, 'graph.graphml')