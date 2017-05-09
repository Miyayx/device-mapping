# -*- coding:utf-8 -*-

import sys

from fileio import *
import numpy as np

def result_account_statistic(fn):
    """
    对私有设备结果做统计
    1. 一共有多少个账号(有私有设备)，其中各类账号的数量与比例
    2. 平均每个AD下有多少“人”(子图)
    3. 平均每个“人”有多少个mdn
    4. 平均每个“人”有多少个qq
    5. 平均每个“人”有多少个设备
    6. 平均每个“人”有多少个手机设备
    7. 总共有多少个私有设备
    8. 总共生成多少个私有设备-账号关系
    """

    ad_total = 0
    people_total = 0
    qq_people = 0
    mdn_people = 0
    people_account_total = 0
    people_mdn_total = 0
    people_qq_total = 0
    people_device_total = 0
    people_phone_total = 0
    account_type_set = {}
    account_type_device_num = {}
    private_device_num = 0
    private_device_account_num = 0

    people_list = []
    mdn_list = []
    qq_list = []
    phone_list = []
    device_list = []

    for ad, graphs in ad_private_device_generator(fn):
        ad_total += 1
        people_total += len(graphs)
        people_list.append(len(graphs))

        for graph in graphs:
            accounts = [n for n in graph if n.split("#")[-1] != "d"]
            people_account_total += len(accounts)

            qqs = [n for n in graph if n.split("#")[-1] == "001_92"]
            if len(qqs):
                qq_list.append(len(qqs))
                qq_people += 1
            people_qq_total += len(qqs)

            mdns = [n for n in graph if n.split("#")[-1] == "001_80"]
            if mdns:
                mdn_list.append(len(mdns))
                mdn_people += 1
            people_mdn_total += len(mdns)

            devices = [n for n in graph if n.split("#")[-1] == "d"]
            people_device_total += len(devices)
            device_list.append(len(devices))

            phones = [n for n in graph if n.split("#")[-1] == "d" and not n.split("@")[0] == "Other"]
            if phones:
                phone_list.append(len(phones))
            people_phone_total += len(phones)

            private_device_num += len(devices)
            private_device_account_num += (len(accounts) * len(devices))

            for account in accounts:
                a, t = account.rsplit("#", 1)
                if not t in account_type_set:
                    account_type_set[t] = set()
                account_type_set[t].add(a)
                account_type_device_num[t] = account_type_device_num.get(t, 0) + len(devices)

    account_total = sum([len(v) for v in account_type_set.values()])
    print "Total account: %d" % account_total
    print {(k, len(v)) for k, v in account_type_set.iteritems()}
    print {(k, len(v) * 1.0 / account_total) for k, v in account_type_set.iteritems()}

    print "people total: %d"%people_total
    print "mdn people total: %d"%mdn_people
    print "qq people total: %d"%qq_people

    print "people/ad: %f"%(people_total * 1.0 / ad_total)
    print "people/ad min %f"%np.min(people_list)
    print "people/ad max %f"%np.max(people_list)
    print "people/ad median %f"%np.median(people_list)
    counts = np.bincount(people_list)
    print "people/ad most %f"%np.argmax(counts)

    print "mdn/people: %f"%(people_mdn_total * 1.0 / mdn_people)
    print "mdn/people min %f"%np.min(mdn_list)
    print "mdn/people max %f"%np.max(mdn_list)
    print "mdn/people median %f"%np.median(mdn_list)
    counts = np.bincount(mdn_list)
    print "mdn/people most %f"%np.argmax(counts)

    print "qq/people: %f"%(people_qq_total * 1.0 / qq_people)
    print "qq/people min %f"%np.min(qq_list)
    print "qq/people max %f"%np.max(qq_list)
    print "qq/people median %f"%np.median(qq_list)
    counts = np.bincount(qq_list)
    print "qq/people most %f"%np.argmax(counts)

    print "mdn/ad: %f"%(people_mdn_total * 1.0 / ad_total)
    print "qq/ad: %f"%(people_qq_total * 1.0 / ad_total)
    print "account/people: %f"%(people_account_total * 1.0 / people_total)

    print "phone/people: %f"%(people_phone_total * 1.0 / people_total)
    print "phone/people min %f"%np.min(phone_list)
    print "phone/people max %f"%np.max(phone_list)
    print "phone/people median %f"%np.median(phone_list)
    counts = np.bincount(phone_list)
    print "phone/people most %f"%np.argmax(counts)

    print "device/people: %f"%(people_device_total * 1.0 / people_total)
    print "device/people min %f"%np.min(device_list)
    print "device/people max %f"%np.max(device_list)
    print "device/people median %f"%np.median(device_list)
    counts = np.bincount(device_list)
    print "device/people most %f"%np.argmax(counts)

    print "private device num: %d"%private_device_num
    print "private device - account num: %d"%private_device_account_num

def public_device_statistics(fn):
    pass


if __name__ == "__main__":
    result_account_statistic(PRIVATE_DEVICE_FN)
    #result_account_statistic(PRIVATE_GRAPH_CROSS_AD_FN)
    public_device_statistics(PUBLIC_DEVICE_FN)

