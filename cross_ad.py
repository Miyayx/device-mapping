# -*- coding:utf-8 -*-

from fileio import *
from utils import *
from models import *

import sys

def generate_ad_account_graph(fn, not_family_ads, ad_shareddevices):

    nodes = dict()
    edges = dict()

    for line in open(fn):
        ad, device, os_, ua, ext_id, pro_category, count = line.strip('\n').split('\001')

        if ad in not_family_ads:
            continue

        if ad in ad_shareddevices and device in ad_shareddevices[ad]:
            continue

        if ext_id =="GWDew2r+Bdw=" or ext_id == "000000000000000" or ext_id == "THze3tVrY0o=" or ext_id == "111111111111111":
            continue

        pro_category = get_type_code(pro_category)

        adn = nodes.get(ad, ADNode(ad))
        nodes[ad] = adn
        an = nodes.get(ext_id, AccountNode(ext_id, pro_category))
        nodes[ext_id] = an

        if not adn in edges:
            edges[adn] = dict()
        if not an in edges:
            edges[an] = dict()
        edges[adn][an] = edges[adn].get(an, 0) + int(count)
        edges[an][adn] = edges[an].get(adn, 0) + int(count)

    nodes = set(nodes.valus())
    graphs = []

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
            for nnn in edges[nn]:
                if nnn.visited == True:
                    continue
                if edges[nn][nnn] >= 1:
                    nnn.visited = True
                    queue.append(nnn)

        graphs.append(graph)

    fw = open("output_2016101112/ad_account_graph", "w")
    for graph in graphs:
        fw.write(ad + "\t" + ";".join([str(n) for n in graph]) + "\n")
    fw.close()

    return graphs

def generate_ad_account_graph2(fn, not_family_ads, ad_shareddevices):

    nodes = dict()
    edges = dict()

    line_count = 0
    for line in open(fn):
        line_count += 1

        if line_count % 10000 == 0:
            sys.stdout.write("%dth line\r"%line_count)
            sys.stdout.flush()

        ad, device, os_, ua, ext_id, pro_category, count = line.strip('\n').split('\001')

        if ad in not_family_ads:
            continue

        if ad in ad_shareddevices and device in ad_shareddevices[ad]:
            continue

        if ext_id =="GWDew2r+Bdw=" or ext_id == "000000000000000" or ext_id == "THze3tVrY0o=" or ext_id == "111111111111111":
            continue

        pro_category = get_type_code(pro_category)

        ad = ad+"#ad"
        nodes[ad] = False
        _id = ext_id+"#"+pro_category
        nodes[_id] = False

        if not ad in edges:
            edges[ad] = dict()
        if not _id in edges:
            edges[_id] = dict()
        edges[ad][_id] = edges[ad].get(_id, 0) + int(count)
        edges[_id][ad] = edges[_id].get(ad, 0) + int(count)

    graphs = []

    print "nodes len:", len(nodes)

    for n in nodes:
        if nodes[n] == True:
            continue
        queue = []
        graph = []
        nodes[n] = True
        queue.append(n)
        while queue:
            nn = queue.pop(0)
            graph.append(nn)
            for nnn in edges[nn]:
                if nodes[nnn] == True:
                    continue
                if edges[nn][nnn] >= 1:
                    nodes[nnn] = True
                    queue.append(nnn)

        if len([g for g in graph if g.split("#")[1] == "ad"]) == 1: #只有一个ad，没有分析价值
            continue
        graphs.append(graph)
        if len(graphs)%100 == 0:
            print "graph num:", len(graphs)

    fw = open("output_2016101112/ad_account_graph", "w")
    for graph in graphs:
        fw.write(ad + "\t" + ";".join([str(n) for n in graph]) + "\n")
    fw.close()

    return graphs

def generate_ad_account_graph3(fn, not_family_ads, ad_shareddevices):

    nodes = dict()
    edges = dict()

    count = 0

    ad_accounts = {}
    ads = []
    account_index = {}
    index = 0

    starttime = time.time()

    for ad, account_count in ad_account_generator(fn):

        if ad in not_family_ads:
            continue

        count += 1
        if count%1000 == 0:
            sys.stdout.write("%dth ad\r"%count)
            sys.stdout.flush()
            if count % 10000 == 0:
                print time.time() - starttime
                starttime = time.time()

        ad_accounts[ad] = set()
        for ext_id, c in account_count.items():
            if ext_id =="GWDew2r+Bdw=" or ext_id == "000000000000000" or ext_id == "THze3tVrY0o=" or ext_id == "111111111111111":
                continue
            if not ext_id in account_index:
                account_index[ext_id] = index
                index += 1
            ad_accounts[ad].add(account_index[ext_id])

        if not ad in edges:
            edges[ad] = set()
        for k in nodes:
            #same_account = len(ad_accounts[ad] & ad_accounts[k])
            #if same_account > 0:
            if ad_accounts[ad] & ad_accounts[k]:
                edges[ad].add(k)
                edges[k].add(ad)

        nodes[ad] = False

    graphs = []

    print "nodes len:", len(nodes)

    for n in nodes:
        if nodes[n] == True:
            continue
        queue = []
        graph = []
        nodes[n] = True
        queue.append(n)
        while queue:
            nn = queue.pop(0)
            graph.append(nn)
            for nnn in edges[nn]:
                if nodes[nnn] == True:
                    continue
                if edges[nn][nnn] >= 1:
                    nodes[nnn] = True
                    queue.append(nnn)

        if len(graph) == 1: #只有一个ad，没有分析价值
            continue
        graphs.append(graph)
        if len(graphs)%100 == 0:
            print "graph num:", len(graphs)

    fw = open("output_2016101112/ad_graph", "w")
    for graph in graphs:
        fw.write(ad + "\t" + ";".join([str(n) for n in graph]) + "\n")
    fw.close()

    return graphs


def private_graph_cross_ad2(private_graph_fn, not_family_ad_fn, shared_fn, output):

    not_family_ads = set()
    for f in not_family_ad_fn:
        not_family_ads = not_family_ads.union(load_notfamily_ad(f))

    ad_shareddevices = load_shared_device(shared_fn)

    ad_account_graphs = generate_ad_account_graph3(DATA_FILE, not_family_ads, ad_shareddevices)
    print "ad_account_graphs length:", len(ad_account_graphs)

    ad_privategraphs = {}
    for line in open(private_graph_fn):
        ad, private_graph = line.strip("\n").split("\t")
        if not ad in ad_privategraphs:
            ad_privategraphs[ad] = []
        if len(private_graph.split(";")) > 20:
            continue
        ad_privategraphs[ad].append(set(private_graph.split(";")))

    fw = open(output, "w")

    for graph in ad_account_graphs:

        ad_account = {}

        for i in range(len(graph)-1, -1, -1):
            if graph[i].split("#")[1] == "ad":
                ad = graph[i].split("#")[0]
                if not ad in ad_account:
                    ad_account[ad] = []
                for private_graph in ad_privategraphs[ad]:
                    accounts = set([n for n in private_graph if not n.split("#")[1] == "d"])
                    ad_account[ad].append(accounts)
            else:
                graph.pop(i) #删除账号类的点，只保留ad类的


        cross_nodes = dict()
        cross_edges = dict()

        for i in range(len(graph)):
            for j in range(i+1, len(graph)):
                adi = graph[i]
                adj = graph[j]
                private_graphs_i = ad_privategraphs[adi]
                private_graphs_j = ad_privategraphs[adj]

                for ii in range(len(private_graph_i)):
                    for jj in range(len(private_graphs_j)):
                        id_i = (adi, ii)
                        id_j = (adj, jj)
                        cross_nodes[id_i] = False
                        cross_nodes[id_j] = False
                        if len(ad_account[adi][ii] ^ ad_account[adj][jj]) > 0: #如果有相同的账号
                            distance = len(private_graph_i ^ private_graph_j) * 1.0 / 2
                            if distance >= 1:
                                if not id_i in cross_edges:
                                    cross_edges[id_i] = set()
                                if not id_j in cross_edges:
                                    cross_edges[id_j] = set()
                                cross_edges[id_i].add(id_j)
                                cross_edges[id_j].add(id_i)

        cross_graphs = []

        for n in cross_nodes:
            if cross_nodes[n] == True:
                continue
            queue = []
            graph = []
            cross_nodes[n] = True
            queue.append(n)
            while queue:
                nn = queue.pop(0)
                graph.append(nn)
                for nnn in cross_edges[nn]:
                    if cross_nodes[nnn] == True:
                        continue
                    cross_nodes[nnn] = True
                    queue.append(nnn)

            cross_graphs.append(graph)

        for cross_graph in cross_graphs:
            graph = set()
            for ad, i in cross_graph:
                private_sub_graph = ad_privategraphs[ad][i]
                graph = graph.union([n+"@"+ad if n.split("#")[1] == "d" else n for n in private_sub_graph])
            fw.write(";".join(graph))
            fw.flush()

    fw.close()
        
        

def find_related_ad(fn, output, not_family_ad_fn=[]):

    account_ad_count = {}

    not_family_ads = set()
    for f in not_family_ad_fn:
        not_family_ads = not_family_ads.union([line.strip('\n') for line in open(f)])

    for line in open(fn):
        ad, device, os_, ua, ext_id, pro_category, count = line.strip('\n').split('\001')

        if ad in not_family_ads:
            continue

        if ext_id =="GWDew2r+Bdw=" or ext_id == "000000000000000" or ext_id == "THze3tVrY0o=" or ext_id == "111111111111111":
            continue

        ext_id = ext_id + "#" + get_type_code(pro_category)

        if not ext_id in account_ad_count:
            account_ad_count[ext_id] = {}
        account_ad_count[ext_id][ad] = account_ad_count[ext_id].get(ad, 0) + int(count)

    fw = open(output, "w")
    bad_account_fw = open("bad_accounts.dat", "w")

    too_many_ad = 0
    cross_account = 0
    cross_ads = set()
    for account, ad_count in account_ad_count.iteritems():
        if len(ad_count) == 1:
            continue
        if len(ad_count) > 20:
            bad_account_fw.write(account + "\n")
            continue
        if len(ad_count) > 1:
            cross_account += 1
            fw.write(account + "\t" + ";".join([k + "#" + str(v) for k, v in ad_count.iteritems()]) + "\n")
            fw.flush()
        #if len(ads) > 1 and len(ads) <= 5:
        #    for a in ads:
        #        cross_ads.add(a)
        #if len(ads) > 5:
        #    too_many_ad += 1
    fw.close()
    bad_account_fw.close()
    
    print "account crossing ad", cross_account
    print "account with too many ad", too_many_ad
    print "cross ads from 1 to 5", len(cross_ads)


def private_graph_cross_ad(private_graph_fn, account_cross_ad_fn, output):

    fw = open(output, 'w')

    ad_privategraph = {}
    for line in open(private_graph_fn):
        ad, private_graph = line.strip("\n").split("\t")
        if not ad in ad_privategraph:
            ad_privategraph[ad] = []
        if len(private_graph.split(";")) > 20:
            continue
        ad_privategraph[ad].append(set(private_graph.split(";")))

    print "Finish loading private graph"
    count = 0
    merge_graph_num = 0
    merge_ads = set()
    people = 0
    for line in open(account_cross_ad_fn):
        count += 1
        account, ads = line.strip("\n").split("\t")
        ads = [ad.split("#")[0] for ad in ads.split(";")]
        graphs = []
        for ad in ads:
            if ad in ad_privategraph:
                for graph in ad_privategraph[ad]:
                    if account in graph:
                        graphs.append((ad, graph)) #只对有指定账户的subgraph进行分析
                        people += 1

        merge_graph = []
        for i in range(len(graphs)):
            for j in range(i+1, len(graphs)):
                if len(graphs[i][1] ^ graphs[j][1]) * 1.0 / 2 >= 1:
                    #print graphs[i]
                    #print graphs[j]
                    merge_graph.append((i, j))

        merge_graph_num += len(merge_graph)

        for i, j in merge_graph:
            adi, graphi = graphs[i]
            adj, graphj = graphs[j]
            merge_ads.add(adi)
            merge_ads.add(adj)
            for k in range(len(ad_privategraph[adi])):
                graph = ad_privategraph[adi][k]
                if account in graph:
                    ad_privategraph[adi].pop(k)
                    accounts = [n for n in graphi if not n.split("#")[-1] == "d"]
                    ad_privategraph[adi].append(graph.union(accounts))
                    break
            for k in range(len(ad_privategraph[adj])):
                graph = ad_privategraph[adj][k]
                if account in graph:
                    ad_privategraph[adj].pop(k)
                    accounts = [n for n in graphi if not n.split("#")[-1] == "d"]
                    ad_privategraph[adj].append(graph.union(accounts))
                    break

        if count % 1000  == 0:
            sys.stdout.write("%dth account\r"%count)
            sys.stdout.flush()

    print "merge graph number : %d"%merge_graph_num
    print "merge ad number : %d"%len(merge_ads)
    print "cross ad people : %d"%people

    for ad, graphs in ad_privategraph.iteritems():
        for graph in graphs:
            fw.write(ad + "\t" + ";".join(graph) + "\n")
            fw.flush()
        
    fw.close()

if __name__=="__main__":
    import time
    starttime = time.time()
    find_related_ad(DATA_FILE, ACCOUNT_CROSS_ADS_FN, [NOTFAMILY_FN, BAD_ADS_FN])
    private_graph_cross_ad(PRIVATE_DEVICE_FN, ACCOUNT_CROSS_ADS_FN, PRIVATE_GRAPH_CROSS_AD_FN)
    #private_graph_cross_ad2(PRIVATE_DEVICE_FN, [NOTFAMILY_FN, "bad_ads.dat"], PUBLIC_DEVICE_FN, PRIVATE_DEVICE_FN)
    print("Time Consuming: %d"%(time.time()-starttime))

