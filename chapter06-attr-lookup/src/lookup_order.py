# -*- coding: utf-8 -*-
"""属性查找的完整优先级链：
__getattribute__ -> data descriptor -> 实例 __dict__ -> 类 __dict__ -> __getattr__
每一次访问到底落在哪一层，用事件日志还原出来。"""
import sys

LOG = []


# == 1. 搭一个五层俱全的实验对象
class Traced:
    """第 1 层：__getattribute__ 拦下所有访问；兜底层：__getattr__ 接住落空的名字。"""
    def __getattribute__(self, name):
        LOG.append("GA:" + name)
        return object.__getattribute__(self, name)

    def __getattr__(self, name):
        LOG.append("FB:" + name)
        return "__getattr__ 兜底值"


class DataDesc:
    """有 __set__ = data descriptor，位次比实例 __dict__ 靠前。"""
    def __get__(self, obj, cls):
        return self if obj is None else "data descriptor 的值"

    def __set__(self, obj, v):
        raise AttributeError("data descriptor 只读，实例字典说了不算")


class NonDataDesc:
    """只有 __get__ = non-data descriptor，位次比实例 __dict__ 靠后。"""
    def __get__(self, obj, cls):
        return self if obj is None else "non-data descriptor 的值"


class Demo(Traced):
    dd = DataDesc()
    nd = NonDataDesc()
    plain = "类字典的普通值"


d = Demo()

print("VERSION\t" + sys.version.split()[0])
print("CHAIN -> __getattribute__ > data descriptor > 实例 __dict__ > 类 __dict__ > __getattr__")

# == 2. 同名对拍：每一层压不压得过实例字典
d.__dict__["dd"] = "实例字典的值"          # 直接塞字典，绕开 setattr
d.__dict__["nd"] = "实例字典的值"
print("DD-VS-INST -> " + repr(d.dd))
print("ND-VS-INST -> " + repr(d.nd))
print("PLAIN -> " + repr(d.plain))
print("MISSING -> " + repr(d.no_such))
print("LOG-MISSING -> " + " ".join(LOG))   # 每次访问都先经过 GA，落空才到 FB

# == 3. 类身上访问与实例身上访问拿到的东西不一样
print("CLASS-GET-IS-DESC -> " + str(Demo.dd is Demo.__dict__["dd"]))
print("INST-GET-IS-DESC -> " + str(d.dd is Demo.__dict__["dd"]))
print("INST-DICT-HAS-DD -> " + str("dd" in d.__dict__))
try:
    d.dd = 1                                 # 走 __set__，被 data descriptor 拦下
    print("SET-DD -> 居然写进去了")
except AttributeError as e:
    print("SET-DD -> AttributeError: " + str(e))
