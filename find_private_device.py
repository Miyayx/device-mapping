# -*- coding:utf-8 -*-

import sys
from sklearn.cluster import DBSCAN

from fileio import *
from models import *
from id_distance import *

"""
联通图方法
"""

def generate_graph(behavior_count, account_type, shared_devices):

    nodes = dict()
    edges = dict()

    for b, c in behavior_count.iteritems():
        d, a = b
        if d in shared_devices:
            continue

        dn = nodes.get(d, DeviceNode(d))
        nodes[d] = dn
        an = nodes.get(a, AccountNode(a, account_type[a]))
        nodes[a] = an

        if not dn in edges:
            edges[dn] = dict()
        if not an in edges:
            edges[an] = dict()
        edges[dn][an] = c
        edges[an][dn] = c

    return set(nodes.values()), edges

MINIMUM_WEIGHT=1

def find_private_graph(behavior_count, account_type, shared_devices):
    """
    In one ad
    这里有两个bug，一个是Node生成的相同devicestring的node，也不被看成是一个，他们是不同的id
    另一个是没在append前把状态改为True，导致在for循环中又一次访问它，又一次被放进了queue中

    把账号和设备都看作点，找联通图，每个子图为一个“人”
    
    """

    nodes, edges = generate_graph(behavior_count, account_type, shared_devices)

    graphs = []

    nodeN = 0
    for n in nodes:
        if n.visited == True:
            continue
        queue = []
        graph = []
        n.visited = True
        queue.append(n)
        while queue:
            nn = queue.pop(0)
            graph.append(nn)
            nodeN += 1
            for nnn in edges[nn]:
                if nnn.visited == True:
                    continue
                if edges[nn][nnn] >= MINIMUM_WEIGHT:
                    nnn.visited = True
                    queue.append(nnn)

        graphs.append(graph)

    assert len(nodes) == nodeN

    return graphs


"""
聚类方法
"""
def find_private_devices(behavior_count, account_type, shared_devices):
    
    #for b, c in behavior_count.items():
    #    d, a = b
    #    if d in shared_devices:
    #        behavior_count.pop(b)

    #if len(behavior_count) == 0:
    #    return []

    devices, similar_matrix = calculate_device_distance(behavior_count)
    dbscan = DBSCAN(eps=0.85, min_samples=2, metric='precomputed')
    labels = dbscan.fit(similar_matrix).labels_
    cluster_n = max(labels)
    for i in range(len(labels)):
        if labels[i] == -1:
            cluster_n += 1
            labels[i] = cluster_n
    device_index = dict((devices[i], i) for i in range(len(devices)))
    account_clusters = {} #账号可能属于多个cluster，找行为数量最多的那个
    for b, c in behavior_count.items():
        d, a = b
        if d in shared_devices:
            continue
        if not a in account_clusters:
            account_clusters[a] = dict()
        label = labels[device_index[d]]
        account_clusters[a][label] = account_clusters[a].get(label, 0) + c

    cluster_graph = {}
    for i in range(len(devices)):
        if devices[i] in shared_devices:
            continue
        if not labels[i] in cluster_graph:
            cluster_graph[labels[i]] = set()
        cluster_graph[labels[i]].add(devices[i]+"#d")

    for a, clusters in account_clusters.iteritems():
        a = a + "#" + account_type[a]
        if len(clusters) == 1:
            cluster_graph[clusters.keys()[0]].add(a)
        else:
            max_c = max(clusters.items(), key=lambda x:x[1])[0]
            cluster_graph[max_c].add(a)

    return cluster_graph.values()
        

def main(fn, shared_fn, notfamily_fn, output):

    ad_shareddevices = load_shared_device(shared_fn)
    not_family_ads = load_notfamily_ad(notfamily_fn)

    count = 0
    fw = open(output, 'w')
    for ad, behavior_count, account_type in ad_info_generator(fn, account_minimum=0):

        if ad in not_family_ads:
            continue

        count += 1
        if count%1000 == 0:
            sys.stdout.write("%dth ad\r"%count)
            sys.stdout.flush()
        
        graphs = find_private_graph(behavior_count, account_type, ad_shareddevices.get(ad, []))
        for graph in graphs:
            fw.write(ad + "\t" + ";".join([str(n) for n in graph]) + "\n")

    fw.close()

def main2(fn, shared_fn, notfamily_fn, output):

    ad_shareddevices = load_shared_device(shared_fn)
    not_family_ads = load_notfamily_ad(notfamily_fn)

    count = 0
    fw = open(output, 'w')
    for ad, behavior_count, account_type in ad_info_generator(fn, account_minimum=0):

        if ad in not_family_ads:
            continue

        count += 1
        if count%1000 == 0:
            sys.stdout.write("%dth ad\r"%count)
            sys.stdout.flush()
        
        graphs = find_private_graph(behavior_count, account_type, ad_shareddevices.get(ad, []))
        graphs2 = find_private_devices(behavior_count, account_type, ad_shareddevices.get(ad, []))

        if(len(graphs) != len(graphs2)):
            fw.write("* unicom %d"%len(graphs) + '\n')
            #print len(graphs), str(graphs)
            for graph in graphs:
                fw.write(ad + "\t" + ";".join([str(n) for n in graph]) + "\n")

            fw.write("* dbscan %d"%len(graphs2) + '\n')
            #print len(graphs2), str(graphs2)
            for graph in graphs2:
                fw.write(ad + "\t" + ";".join([str(n) for n in graph]) + "\n")

            fw.write(("=" * 20) + "\n")
            fw.flush()

    fw.close()


if __name__ == "__main__":
    import time
    #main("ad_all_device_account_2016/test.dat", "shared_device.dat", "private_graph.dat")
    start_time = time.time()
    main2(DATA_FILE, PUBLIC_DEVICE_FN, NOTFAMILY_FN, "private_graph_compare.addshared.dat")
    print("Time Consuming: %d"%(time.time()-start_time))
