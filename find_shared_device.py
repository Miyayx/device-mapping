# -*- coding:utf-8 -*-

from id_distance import *
from fileio import *
from utils import *

import sys

#同类型账号大于等于规定数量的就算共享设备
SAME_TYPE_ACCOUNT = {QQ_PRO:5, MDN_PRO:4, IMEI_PRO:3, TDID_PRO:2}
PEOPLE_NUMBER = 3
MAXIMAX_ACCOUNT_IN_CLUSTER = 5
ACCOUNT_DISTANCE = 0.85
NOTFAMILY_SHARED_DEVICE_COUNT = 3

class Node:
    def __init__(self):
        self.node_list = set()

    def merge(self, node):
        n = Node()
        n.node_list = self.node_list.union(node.node_list)
        return n

    def is_terminate(self):
        if len(self.node_list) > MAXIMAX_ACCOUNT_IN_CLUSTER:
            return True
        return False

    def __str__(self):
        return str(self.node_list)


def get_device_accounttype(behavior_count, account_type):
    """
    """
    device_accounttype_num = {}
    for b, c in behavior_count.items():
        d, a = b
        if not d in device_accounttype_num:
            device_accounttype_num[d] = {}
        t = account_type[a]
        device_accounttype_num[d][t] = device_accounttype_num[d].get(t, 0) + 1

    return device_accounttype_num

#def do_cluster(nodes):
#    # make a copy, do not touch the original list
#    nodes = nodes[:]
#    while len(nodes) > 1:
#        print "Clustering [%d]..." % len(nodes)
#        min_distance = float('inf')
#        min_pair = (-1, -1)
#        for i in range(len(nodes)):
#            for j in range(i+1, len(nodes)):
#                distance = nodes[i].distance(nodes[j])
#                if distance < min_distance:
#                    min_distance = distance
#                    min_pair = (i, j)
#        i, j = min_pair
#        node1 = nodes[i]
#        node2 = nodes[j]
#        del nodes[j] # note should del j first (j > i)
#        del nodes[i]
#        nodes.append(node1.merge(node2, min_distance))
# 
#    return nodes[0]

def do_cluster(distance_matrix):

    nodes = []
    for i in range(len(distance_matrix)):
        node = Node()
        node.node_list.add(i)
        nodes.append(node)

    #nodes = [Node(a) for a in accounts]
    #account_index = dict((a, i) for i, a in enumerate(accounts))

    def get_distance(n1, n2):
        md = float('inf')
        for ni in n1.node_list:
            for nj in n2.node_list:
                dist = distance_matrix[ni][nj]
                if dist < md:
                    md = dist
        return md


    while len(nodes) > 1:
        min_distance = float('inf')
        min_pair = (-1, -1)
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                distance = get_distance(nodes[i], nodes[j]) 
                if distance > ACCOUNT_DISTANCE:
                    continue
                if distance < min_distance:
                    min_distance = distance
                    min_pair = (i, j)
        i, j = min_pair
        if i == -1 or j == -1:
            break
        node1 = nodes[i]
        node2 = nodes[j]
        del nodes[j] # note should del j first (j > i)
        del nodes[i]
        new_node = node1.merge(node2)
        nodes.append(new_node)
        if new_node.is_terminate():
            break

    clusters = [ n.node_list for n in nodes]
    return clusters


def find_shared_device(behavior_count, account_type):
    """
    In one ad
    1. 同一类型的账号出现$SAME_TYPE_ACCOUNT$次及其以上
    2. 不相关(距离大)的账号出现$SIMILAR_ACCOUNT$次及其以上
       2.1 判断账号相关性的条件为： 账号距离小于$ACCOUNT_DISTANCE$的看作同一个人的账号
    """

    shared_devices = []
    device_accounttype_num = get_device_accounttype(behavior_count, account_type)

    # 条件1
    for device, type_num in device_accounttype_num.iteritems():
        for k, v in SAME_TYPE_ACCOUNT.iteritems():
            if k in type_num and type_num[k] >= v:
                shared_devices.append(device)
                break
            
    # 条件2
    accounts, distance_matrix = calculate_account_distance(behavior_count)
    clusters = do_cluster(distance_matrix)
    #account_distance = calculate_account_distance(behavior_count)
    #account_distance_dict = {}
    #accounts = set()
    #for a, distance in account_distance.iteritems():
    #    a1, a2 = a
    #    accounts.add(a1)
    #    accounts.add(a2)
    #    if not a1 in account_distance_dict:
    #        account_distance_dict[a1] = {}
    #    if not a2 in account_distance_dict:
    #        account_distance_dict[a2] = {}
    #    account_distance_dict[a1][a2] = distance
    #    account_distance_dict[a2][a1] = distance

    #for i in range(len(accounts)):
    #    for j in range(i+1, len(accounts)):
    #        dist = distance_matrix[i][j]
    #        a1, a2 = accounts[i], accounts[j]
    #        if not a1 in account_distance_dict:
    #            account_distance_dict[a1] = {}
    #        if not a2 in account_distance_dict:
    #            account_distance_dict[a2] = {}
    #        account_distance_dict[a1][a2] = dist
    #        account_distance_dict[a1][a2] = dist

    #clusters = []

    #visited_accounts = set()
    #for a in accounts:
    #    if a in visited_accounts:
    #        continue
    #    queue = []
    #    cluster = []
    #    visited_accounts.add(a)
    #    queue.append(a)
    #    while queue:
    #        aa = queue.pop(0)
    #        cluster.append(aa)
    #        for aaa in account_distance_dict[aa]:
    #            if aaa in visited_accounts:
    #                continue
    #            if account_distance_dict[aa][aaa] <= ACCOUNT_DISTANCE:
    #                visited_accounts.add(aaa)
    #                queue.append(aaa)
    #    clusters.append(cluster)

    aid_clusterid = {}
    for i in range(len(clusters)):
        for ai in clusters[i]:
            aid_clusterid[ai] = i

    del clusters
        
    ##account_similaraccount = {}
    ##for a, distance in account_distance.iteritems():
    ##    a1, a2 = a
    ##    if not a1 in account_similaraccount:
    ##        account_similaraccount[a1] = set()
    ##    if not a2 in account_similaraccount:
    ##        account_similaraccount[a2] = set()
    ##    if distance <= 0.5:
    ##        account_similaraccount[a1].add(a2)
    ##        account_similaraccount[a2].add(a1)

    device_clusterid = {}
    for b, c in behavior_count.iteritems():
        d, a = b
        if d in shared_devices:
            continue
        if not d in device_clusterid:
            device_clusterid[d] = set()
        ci = aid_clusterid[accounts.index(a)]
        if not ci in device_clusterid[d]:
            device_clusterid[d].add(ci)
            if len(device_clusterid[d]) >= PEOPLE_NUMBER:
                shared_devices.append(d)

    return shared_devices


def main(fn, output, notfamily_fn=None):
    import time
    starttime = time.time()

    fw = open(output, "w")
    nfamily_fw = open(notfamily_fn, "w")

    count = 0
    have_shared_count = 0

    for ad, behavior_count, account_type in ad_info_generator(fn, record_bad_ads=True):
        
        if len(behavior_count) == 0:
            break

        count += 1
        if count%1000 == 0:
        #    print("%dth ad"%count)
            sys.stdout.write("%dth ad\r"%count)
            sys.stdout.flush()
            if count%10000 == 0:
                print("Time Consuming: %f"%(time.time()-starttime))
        
        shared_devices = find_shared_device(behavior_count, account_type)

        if len(shared_devices) > NOTFAMILY_SHARED_DEVICE_COUNT:
            nfamily_fw.write(ad+"\n")
            nfamily_fw.flush()
            continue #非家庭的公有设备不做记录

        if len(shared_devices) > 0:
            have_shared_count += 1
            fw.write(ad + "\t" + ";".join(shared_devices) + "\n")
            fw.flush()

    print("%d/%d have shared device ad / calculate ad"%(have_shared_count, count))

    fw.close()
    nfamily_fw.close()

if __name__ == "__main__":
    main(DATA_FILE, PUBLIC_DEVICE_FN, NOTFAMILY_FN)

