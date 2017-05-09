# -*- coding:utf-8 -*-

class DeviceNode:
    def __init__(self, string):
        self.name = string
        self.type = "d"
        self.visited = False

    def __str__(self):
        return str(self.name + "#" + self.type)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

class AccountNode:
    def __init__(self, string, t):
        self.name = string
        self.type = t
        self.visited = False

    def __str__(self):
        return str(self.name + "#" + self.type)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

class ADNode:
    def __init__(self, string):
        self.name = string
        self.type = "ad"
        self.visited = False

    def __str__(self):
        return str(self.name + "#" + self.type)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

