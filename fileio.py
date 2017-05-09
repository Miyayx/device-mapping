# -*- coding:utf-8 -*-

import  os
import sys

from utils import *

#DIR = "output_2016101112"
DIR = "output_111201"
#DIR = "output_120102"
#DIR = "output_2017010203"
#DIR = "output_2016091011"
#DIR = "output_2016101112_dbscan"

#DATA_FILE = "ad_device_account_count_2016101112/000000_0"
DATA_FILE = "ad_device_account_count_111201/000000_0"
#DATA_FILE = "ad_device_account_count_120102/000000_0"
#DATA_FILE = "ad_device_account_count_2017010203/000000_0"
#DATA_FILE = "ad_device_account_count_2016091011/000000_0"

BAD_ADS_FN=os.path.join(DIR, "bad_ads.dat")
PRIVATE_DEVICE_FN=os.path.join(DIR, "private_graph.dat")
PRIVATE_DEVICE_FN_2=os.path.join(DIR, "private_graph_2.dat")
PUBLIC_DEVICE_FN=os.path.join(DIR,"shared_device.dat")
PUBLIC_DEVICE_ACCOUNT_FN=os.path.join(DIR, "shared_device_account.dat")
NOTFAMILY_FN = os.path.join(DIR, "notfamily.dat")
DEVICE_MAPPING_OUTPUT=os.path.join(DIR, "device_mapping_output.dat")
ACCOUNT_DEVICE_OUTPUT=os.path.join(DIR, "account_device_output.dat")

ACCOUNT_CROSS_ADS_FN=os.path.join(DIR, "account_cross_ads.dat")
PRIVATE_GRAPH_CROSS_AD_FN=os.path.join(DIR, "private_graph_cross_ad.dat")

ACCOUNT_DEVICE_OUTPUT_CROSSAD=os.path.join(DIR, "account_device_output_crossad.dat")
DEVICE_MAPPING_OUTPUT_CROSSAD=os.path.join(DIR, "device_mapping_output_crossad.dat")

FAMILY_PEOPLENUM_FN=os.path.join(DIR, "family_peoplenum.dat")

ACCOUNT_MINIMUM = 2
DEVICE_MAXIMUM = 100
ACCOUNT_MAXIMUM = 500

def ad_info_generator(fn, record_bad_ads=False, account_minimum=2, account_maximum=500, device_maximum=100):
    """
    不输出<=2个账号的ad(据统计此类ad大概占30%)
    不算设备数量大于$Device_MAXIMUM$的
    不算账号数量大于$ACCOUNT_MAIMUM$的
    """

    current_ad = ""
    behavior_count = {}
    accounts = set()
    devices = set()
    account_type = {}

    ad_total = 0
    not_calculate_ad_num = 0
    less_account_ad = 0
    many_account_ad = 0
    many_device_ad = 0

    fw = None
    if record_bad_ads:
        fw = open(BAD_ADS_FN, "w")

    for line in open(fn):
        ad, device, os_, ua, ext_id, pro_category, count = line.strip('\n').split('\001')
        if not ad == current_ad:
            ad_total += 1
            if len(current_ad) > 0 and len(accounts) > account_minimum and len(devices) <= device_maximum and len(accounts) <= account_maximum:
                yield current_ad, behavior_count, account_type

            if len(accounts) <= account_minimum:
                less_account_ad += 1
            if len(accounts) > account_maximum:
                many_account_ad += 1
                if fw:
                    fw.write(ad+"\n")
            if len(devices) > device_maximum:
                many_device_ad += 1
            if len(accounts) <= account_minimum or len(accounts) > account_maximum or len(devices) > device_maximum:
                not_calculate_ad_num += 1

            current_ad = ad
            behavior_count = {}
            accounts = set()
            devices = set()
            account_type = {}

        pro_category = get_type_code(pro_category)

        account_type[ext_id] = pro_category
        accounts.add(ext_id)

        device_string = get_device_string(device, os_, ua)
        devices.add(device_string)
        #key = (device_string, ext_id, pro_category)
        key = (device_string, ext_id)
        if count.isdigit():
            behavior_count[key] = behavior_count.get(key, 0) + int(count)

    print("<=2 account ad: %d"%less_account_ad)
    print("many account ad: %d"%many_account_ad)
    print("many device ad: %d"%many_device_ad)
    print("%d/%d not_calculate/total_ad"%(not_calculate_ad_num, ad_total))

    if fw:
        fw.close()

    yield current_ad, behavior_count, account_type


def load_shared_device(shared_fn):

    ad_shareddevices = {}

    for line in open(shared_fn):
        ad, devices = line.strip('\n').split('\t')
        devices = set(devices.split(';'))
        ad_shareddevices[ad] = devices

    return ad_shareddevices

def load_notfamily_ad(notfamily_fn):
    return set([line.strip('\n') for line in open(notfamily_fn)])

def ad_account_generator(fn, account_maximum=200):
    """
    ad 及其下面的账号和次数
    """

    current_ad = ""
    account_count = {}

    ad_total = 0

    for line in open(fn):
        ad, device, os_, ua, ext_id, pro_category, count = line.strip('\n').split('\001')
        if not ad == current_ad:
            ad_total += 1
            if len(current_ad) > 0 and len(account_count) <= account_maximum:
                yield current_ad, account_count

            current_ad = ad
            account_count = {}

        pro_category = get_type_code(pro_category)

        key = ext_id + "#" + pro_category
        account_count[key] = account_count.get(key, 0) + int(count)

    yield current_ad, account_count


def ad_private_device_generator(fn):
    """
    Reading private_device.dat
    """

    current_ad = ""
    graphs = []

    ad_total = 0

    for line in open(fn):
        ad, graph = line.strip('\n').split('\t')

        if not ad == current_ad:

            ad_total += 1
            if ad_total%1000 == 0:
                sys.stdout.write("%dth ad\r"%ad_total)
                sys.stdout.flush()

            if len(current_ad) > 0:
                yield current_ad, graphs

            current_ad = ad
            graphs = []

        graphs.append(graph.split(";"))

    yield current_ad, graphs

