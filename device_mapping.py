# -*- coding:utf-8 -*-

import os

DIR = ""
for f in os.listdir(DIR):
    for line in open(os.path.join(DIR, f)):
        pass
