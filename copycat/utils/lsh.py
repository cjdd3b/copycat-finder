"""
lsh.py

Algorithms based on 'Mining of Massive Datasets'
"""
from unionfind import UnionFind


class Signature:
    """Signature Base class."""

    def __init__(self, dim):
        self.dim = dim
        self.hashes = self.hash_functions()

    def hash_functions(self):
        """Returns dim different hash functions"""
        pass

    def sign(self, object):
        """Return the signature for object s"""
        pass


class MinHashSignature(Signature):
    """Creates signatures for sets/tuples using minhash."""

    def hash_functions(self):
        """Return dim different hash functions"""
        def hash_factory(n):
            return lambda x: hash("salt" + str(n) + str(x) + "salt")
        return [ hash_factory(_) for _ in range(self.dim) ]
    
    def sign(self, s):
        """Returns minhash signature for set s"""
        sig = [ float("inf") ] * self.dim
        for hash_ix, hash_fn in enumerate(self.hashes):
            sig[hash_ix] = min(hash_fn(value) for value in s)
        return sig        


class LSH:
    """Locality sensitive hashing.  Uses a banding approach to hash
    similar signatures to the same buckets."""
    def __init__(self, length, threshold):
        self.length = length
        self.threshold = threshold
        self.bandwidth = self.get_bandwidth(length, threshold)

    def hash(self, sig):
        """Generate hashvals for this signature"""
        for band in zip(*(iter(sig),) * self.bandwidth):
            yield hash("salt" + str(band) + "tlas")
        
    def get_bandwidth(self, n, t):
        """Approximates the bandwidth (number of rows in each band)
        needed to get threshold.  
        
        Threshold t = (1/b) ** (1/r) where
        b = #bands
        r = #rows per band
        n = b * r = #elements in signature
        """
        
        best = n, 1
        minerr  = float("inf")
        for r in range(1, n + 1):
            try:
                b = 1. / (t ** r)
            except:             # Divide by zero, your signature is huge
                return best
            err = abs(n - b * r)
            if err < minerr:
                best = r
                minerr = err
        return best

    def get_threshold(self):
        r = self.bandwidth
        b = self.length / r
        return (1. / b) ** (1. / r)


class Cluster:
    """Clusters sets with Jaccard similarity above threshold with high
    probability.

    Algorithm based on Rajaraman, "Mining of Massive Datasets":
    1. Generate set signature
    2. Use LSH to map similar signatures to same buckets
    3. Use UnionFind to merge buckets containing same values
    """
    def __init__(self, width=10, threshold=0.5):
        self.width = width
        self.unionfind = UnionFind()
        self.signer = MinHashSignature(width)
        self.hasher = LSH(width, threshold)
        self.hashmap = {}

    def add_set(self, s, label=None):
        # A label for this set
        if not label:
            label = s

        # Add to unionfind structure
        self.unionfind[label]

        # Get signature
        sig = self.signer.sign(s)

        # Union labels with same LSH keys
        for hshval in self.hasher.hash(sig):
            self.hashmap.setdefault(hshval, []).append(label)
            self.unionfind.union(label, self.hashmap[hshval][0])

    def get_sets(self):
        return self.unionfind.sets()

########## HELPER FUNCTIONS ###########

def shingle(word, n):
    '''
    Not using a generator here, unlike the initial implementation,
    both because it doesn't save a ton of memory in this use case
    and because it was borking the creation of minhashes.
    '''
    return set([word[i:i + n] for i in range(len(word) - n + 1)])

def jaccard_sim(X, Y):
    """Jaccard similarity between two sets"""
    x = set(X)
    y = set(Y)
    return float(len(x & y)) / len(x | y)
