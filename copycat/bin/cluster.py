import numpy
import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans, MiniBatchKMeans
from gensim import similarities, corpora, models
from gensim.similarities.docsim import Similarity
from apps.bills.models import Bill

########## CONSTANTS ##########

K_CLUSTERS = 25

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
    # Get the bills and bill text from the database. Also force early evaluation of
    # the queryset so its contents can be accessed without database queries later.
    bills = list(Bill.objects.all())
    billtext = Bill.objects.all().values_list('title', flat=True)
    
    # Get word counts for bill titles
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(billtext)

    # Transform word counts into tf-idf vectors, for feeding into K-Means
    tf_transformer = TfidfTransformer().fit(X_train_counts)
    X_train_tf = tf_transformer.transform(X_train_counts)

    # Execute minibatch k-means on the tf-idf vectors. Using minibatch because it runs
    # orders of magnitude faster than traditional k-means, at the expense of a little precision
    print '---------- Forming %s initial clusters ----------' % K_CLUSTERS
    km = MiniBatchKMeans(n_clusters=K_CLUSTERS, init='k-means++', n_init=1, compute_labels=True)
    km_results = km.fit(X_train_tf)

    G = nx.Graph() # Prep an empty networkX graph for later

    # Iterate through each of the k-means clusters
    for i in range(K_CLUSTERS):
        # Lists containing bill text and the bill object's position in the above array. This is super hacky
        # and could definitely stand to be cleaned up.
        bill_ids = numpy.where(km_results.labels_ == i)[0]
        clustertext = [billtext[id] for id in bill_ids]

        print '---------- Processing cluster %s of %s (%s items) ----------' % (i + 1, K_CLUSTERS, len(clustertext))

        # Load titles into gensim dictionary object
        dictionary = corpora.Dictionary(line.lower().split() for line in clustertext)

        # Now create corpus and tfidf model
        bc = BillCorpus(clustertext, dictionary)
        tfidf = models.TfidfModel(bc)

        # Create and iterate over the similarity matrix
        index = Similarity(corpus=tfidf[bc], num_features=tfidf.num_nnz, output_prefix="shard")
        for i in enumerate(index):
            for j in numpy.nonzero(i[1] > 0.7)[0]:
                id1, id2 = bill_ids[[i[0]]], bill_ids[j]
                bill1, bill2 = bills[id1], bills[id2]
                if bill1.state <> bill2.state:
                    G.add_node(bill1.title, state=bill1.state.name, session=bill1.session.name, bill_id=bill1.bill_id)
                    G.add_node(bill2.title, state=bill2.state.name, session=bill2.session.name, bill_id=bill2.bill_id)
                    G.add_edge(bill1.title, bill2.title)

    # Write matches to a graphml file for processing in Gephi
    nx.write_graphml(G, 'output/kgraph%s.graphml' % K_CLUSTERS)