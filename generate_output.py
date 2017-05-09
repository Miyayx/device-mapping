# -*- coding:utf-8 -*-

from utils import *
from fileio import *

import md5

def public_device_account(data_file, public_device_fn, public_device_account_fn):

    public_device_num = 0
    public_device_behavior_count = 0
    public_device_accounts = set()

    fw = open(public_device_account_fn, "w")
    shared_devices = {}
    for line in open(public_device_fn):
        ad, devices = line.strip('\n').split('\t')
        shared_devices[ad] = set(devices.split(";"))
        public_device_num += len(shared_devices[ad])
    
    print "%d ads have shared devices"%len(shared_devices)
    print "%d shared devices"%public_device_num

    count = 0
    for ad, behavior_count, account_type in ad_info_generator(data_file):
        count += 1
        if ad in shared_devices:
            devices = shared_devices[ad]
            device_accounts = {}
            for d, a in behavior_count.iterkeys():
                if d in devices:
                    public_device_behavior_count += behavior_count[(d,a)]
                    public_device_accounts.add(a)
                    if not d in device_accounts:
                        device_accounts[d] = set()
                    t = account_type[a]
                    device_accounts[d].add(a + "#" + t)
            for d, aset in device_accounts.iteritems():
                fw.write(ad + "\t" + d + "\t" + ";".join(aset) + "\n")
    fw.close()
    print "%d shared devices behavior count"%public_device_behavior_count

def generate_output(private_graph_fn, public_device_account_fn, account_device_output, device_mapping_output = None):
    """
    两个输出文件：
    account_device_output: ad, account, account_type, device, os, device_type(private, public)
    device_mapping_output: did, ad, device, os, device_type(private, public)
    """
    

    fw = open(account_device_output, "w")
    fw2 = None
    if device_mapping_output:
        fw2 = open(device_mapping_output, "w")
    
    account_dids = {}
    for line in open(private_graph_fn):
        ad, graph = line.strip('\n').split("\t")
        devices = []
        accounts = []
        for node in graph.split(";"):
            node, t = node.rsplit("#", 1)
            if t == "d":
                devices.append(node)
            elif t == QQ_PRO:
                accounts.append(node+"#qq")
            elif t == MDN_PRO:
                accounts.append(node+"#mdn")
            elif t == IMEI_PRO:
                accounts.append(node+"#imei")
            elif t == TDID_PRO:
                accounts.append(node+"#tdid")

        if fw2:
            did = md5.md5(";".join([d.replace("@", "#") for d in devices])).digest()
            for d in devices:
                fw2.write("\t".join([did, ad, d.rsplit("@",1)[0], d.rsplit("@", 1)[1], "private"])+"\n")
            fw2.flush()
            for a in accounts:
                if not a in account_dids:
                    account_dids[a] = set()
                account_dids[a].add(did)
    
        for a in accounts:
            for d in devices:
                fw.write("\t".join([ad, a.split("#")[0], a.split("#")[1], d.rsplit("@",1)[0], d.rsplit("@", 1)[1], "private"])+"\n")
        fw.flush()
    
    for line in open(public_device_account_fn):
        ad, device, accounts = line.strip("\n").split("\t")
        accounts = accounts.split(";")
        for a in accounts:
            a = a.replace(QQ_PRO, "qq").replace(MDN_PRO, "mdn").replace(IMEI_PRO, "imei").replace(TDID_PRO, "tdid")
            fw.write("\t".join([ad, a.split("#")[0], a.split("#")[1], d.rsplit("@",1)[0], d.rsplit("@", 1)[1], "public"])+"\n")
        fw.flush()

        if fw2:
            for a in accounts:
                if a in account_dids:
                    for did in account_dids[a]:
                        fw2.write("\t".join([did, ad, d.rsplit("@", 1)[0], d.rsplit("@", 1)[1], "public"]) + "\n")
            fw2.flush()
    
    fw.close()
    if fw2:
        fw2.close()

def statistic_people_in_family(private_graph_fn, family_peoplenum_fn):

    fw = open(family_peoplenum_fn, "w")

    for ad, graphs in ad_private_device_generator(private_graph_fn):
        fw.write(ad + "\t" + str(len(graphs)) + "\n")

    fw.close()

if __name__=="__main__":
    import time
    start_time = time.time()
    #print "public device account"
    #public_device_account(DATA_FILE, PUBLIC_DEVICE_FN, PUBLIC_DEVICE_ACCOUNT_FN)
    #print "generate output ..."
    #generate_output(PRIVATE_DEVICE_FN, PUBLIC_DEVICE_ACCOUNT_FN, ACCOUNT_DEVICE_OUTPUT)
    print "generate cross ad output ..."
    generate_output(PRIVATE_GRAPH_CROSS_AD_FN, PUBLIC_DEVICE_ACCOUNT_FN, ACCOUNT_DEVICE_OUTPUT_CROSSAD, DEVICE_MAPPING_OUTPUT_CROSSAD)
    #statistic_people_in_family(PRIVATE_DEVICE_FN, FAMILY_PEOPLENUM_FN)
    
    print("Time Consuming: %d"%(time.time()-start_time))
