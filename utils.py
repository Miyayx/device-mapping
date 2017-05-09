# -*- utf-8 -*-

QQ_PRO="001_92"
MDN_PRO="001_80"
IMEI_PRO="001_82"
TDID_PRO="001_87"

def get_type_code(pro_category):
    if pro_category.startswith("001_81"):
        pro_category = MDN_PRO
    if pro_category.startswith("001_83"):
        pro_category = IMEI_PRO
    if pro_category.startswith("001_85"):
        pro_category = IMEI_PRO
    return pro_category[:6]

def get_device_string(device, os_, ua):
    #if device == "Other" and os_.startswith("Windows"):
    #    return os_+"@"+ua
    #else:
    #    return device+"@"+os_
    return device+"@"+os_
