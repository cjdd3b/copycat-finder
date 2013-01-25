from utils.lsh import Cluster, shingle
from utils.similarity import shingle
from apps.bills.models import *


if __name__ == '__main__':
    cluster = Cluster(threshold=0.6)
    for bill in Bill.objects.all():
        title = bill.title.encode('utf-8', errors='replace')
        try:
            cluster.add_set(shingle(title, 15), bill)
        except ValueError:
            pass
    for c in cluster.get_sets():
        if not len(c) > 1: continue
        different_states = [i.state for i in c]
        if len(set(different_states)) > 1:
            print c