# -*- coding:utf-8 -*-

import os
from scipy import spatial

from fileio import *

def cosine_distance(v1, v2):
    return spatial.distance.cosine(v1, v2)

def euclidean_distance(v1, v2):
    return spatial.distance.euclidean(v1, v2)

JACCARD_MAX_LOGINNUM = 6
def jaccard_distance_list(v1, v2):

    intersection_n = sum([min(v1[i], v2[i]) for i in range(len(v1))])
    union = sum([min(v, JACCARD_MAX_LOGINNUM) for v in v1]) + sum([min(v, 10) for v in v2])

    return (union - intersection_n) * 1.0 / union

def jaccard_distance_set(v1, v2):

    v1_set = set([i for i in range(len(v1)) if v1[i] > 0])
    v2_set = set([i for i in range(len(v2)) if v2[i] > 0])

    return len(v1_set^v2_set)*1.0/len(v1_set|v2_set)

def cosine_similar(v1, v2):
    return 1 - cosine_distance(v1, v2)

def calculate_account_distance(behavior_count):

    features = list(set(k[0] for k in behavior_count))
    accounts = list(set(k[1] for k in behavior_count))

    #account_distance = {}

    distance_matrix = [[0 for j in range(len(accounts))] for i in range(len(accounts))]

    if len(accounts) <= 2:
        return accounts, distance_matrix
    
    account_vector = {}
    for b, c in behavior_count.items():
        d, a = b
        if not a in account_vector:
            account_vector[a] = [0] * len(features)
        account_vector[a][features.index(d)] += c

    #for i in range(len(accounts)):
    #    for j in range(i+1, len(accounts)):
    #        a1, a2 = accounts[i], accounts[j]
    #        #account_distance[(a1, a2)] = cosine_distance(account_vector[a1], account_vector[a2])
    #        #account_distance[(a1, a2)] = euclidean_distance(account_vector[a1], account_vector[a2])
    #        #account_distance[(a1, a2)] = jaccard_distance_set(account_vector[a1], account_vector[a2])
    #        account_distance[(a1, a2)] = jaccard_distance_list(account_vector[a1], account_vector[a2])

    #return account_distance

    for i in range(len(accounts)):
        for j in range(i+1, len(accounts)):
            a1, a2 = accounts[i], accounts[j]
            distance_matrix[i][j] = jaccard_distance_list(account_vector[a1], account_vector[a2])
            distance_matrix[j][i] = distance_matrix[i][j]

    return accounts, distance_matrix

def account_distance_output(fn, output):
    
    output = open(output, 'w')
    count = 0
    for ad, behavior_count, account_type in ad_info_generator(fn):
        count += 1
        if count >= 1000:
            break
        accounts, distance_matrix = calculate_account_distance(behavior_count)
        for i in range(len(distance_matrix)):
            for j in range(i+1, len(distance_matrix)):
                output.write(ad + "\t" + accounts[i] + "\t" + accounts[j] + "\t" + str(distance_matrix[i][j]) + "\n")
                output.flush()
    output.close()


MINIMUM_DISTANCE_THRESHOLD=0.85
MAXIMUM_DISTANCE_THRESHOLD=1.0

def account_distance_test(fn, output):
    
    output = open(output, 'w')
    count = 0
    for ad, behavior_count, account_type in ad_info_generator(fn):
        count += 1
        if count >= 1000:
            break
        account_distance = calculate_account_distance(behavior_count)
        if len(account_distance) == 0:
            continue
        if len([v for v in account_distance.values() if v > MINIMUM_DISTANCE_THRESHOLD and v < MAXIMUM_DISTANCE_THRESHOLD]) == 0:
            continue
        output.write(ad + "\n\n")
        #output.write("\n".join([str(k)+"\t"+str(v) for k, v in sorted(account_distance.iteritems(), key=lambda x:x[1]) if v > MINIMUM_DISTANCE_THRESHOLD and v < MAXIMUM_DISTANCE_THRESHOLD]) + "\n\n" + \
        #        "\n".join([str(k) + "\t" + str(v) for k, v in behavior_count.items()]) + "\n\n\n")
        for k, v in sorted(account_distance.iteritems(), key=lambda x:x[1]):
            if v > MINIMUM_DISTANCE_THRESHOLD and v < MAXIMUM_DISTANCE_THRESHOLD:
                output.write(str(k) + "\t" + str(v) + "\n")
                for behavior, c in sorted(behavior_count.iteritems(), key=lambda x:x[0][1]):
                    if behavior[1] == k[0] or behavior[1] == k[1]:
                        output.write(str(behavior) + "\t" + str(c) + "\n")
                output.write("\n")

        output.write("\n")
        output.flush()
    output.close()

def calculate_device_distance(behavior_count):

    features = list(set(k[1] for k in behavior_count))
    devices  = list(set(k[0] for k in behavior_count))

    distance_matrix = [[0 for j in range(len(devices))] for i in range(len(devices))]

    device_vector = {}
    for b, c in behavior_count.items():
        d, a = b
        if not d in device_vector:
            device_vector[d] = [0] * len(features)
        device_vector[d][features.index(a)] += c

    for i in range(len(devices)):
        for j in range(i+1, len(devices)):
            d1, d2 = devices[i], devices[j]
            distance = jaccard_distance_list(device_vector[d1], device_vector[d2])
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance_matrix[i][j]

    return devices, distance_matrix

if __name__=="__main__":
    import time
    start_time = time.time()
    account_distance_test("ad_device_account_count_2016101112/000000_0", "account_distance_jaccard_list_0.85.dat")
    print "Time Consuming", time.time() - start_time
    
