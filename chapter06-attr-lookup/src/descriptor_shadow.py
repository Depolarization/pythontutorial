# -*- coding: utf-8 -*-
"""data descriptor 压得过实例字典，non-data 压不过——附 property 子类踩坑实录。"""
import sys


# == 1. 自定义描述符对拍
class ReadOnly:
    def __get__(self, obj, cls):
        return self if obj is None else "描述符的值"

    def __set__(self, obj, v):
        raise AttributeError("只读")


class GetOnly:
    def __get__(self, obj, cls):
        return self if obj is None else "描述符的值"


class C:
    dd = ReadOnly()


c = C()
c.__dict__["dd"] = "实例字典的值"          # 直接塞字典，绕过 __setattr__
print("VERSION\t" + sys.version.split()[0])
print("DATA-VS-INST -> " + repr(c.dd))     # data descriptor 赢


class D:
    nd = GetOnly()


d = D()
d.__dict__["nd"] = "实例字典的值"
print("NONDATA-VS-INST -> " + repr(d.nd))  # 实例字典赢

# == 2. property 就是现成的 data descriptor
class P:
    @property
    def v(self):
        return "P 的 getter"


p = P()
try:
    p.v = 1                                # 没有 setter，赋值直接炸
    print("PROPERTY-NOSETTER -> 写进去了")
except AttributeError as e:
    print("PROPERTY-NOSETTER -> AttributeError: " + str(e))
print("PROPERTY-INST-DICT -> " + str(vars(p)))

# == 3. 踩坑实录：子类重写 getter，父类的 setter 就丢了
class P2:
    @property
    def v(self):
        return "P.get"

    @v.setter
    def v(self, x):
        self._x = x


class Q(P2):
    @property
    def v(self):                           # 新 property 只有 getter
        return "Q.get"


q = Q()
g = q.v
print("SUBCLASS-GET -> " + repr(g))
try:
    q.v = 3
    print("SUBCLASS-SET -> 设置成功")
except AttributeError as e:
    print("SUBCLASS-SET -> AttributeError: " + str(e))
print("PARENT-STILL-WORKS -> ", end="")
pq = P2()
pq.v = 5
print(str(pq._x) + "（父类的 setter 一直都在）")

# == 4. Q.v 仍是 data descriptor，照样压住实例字典
q.__dict__["v"] = "实例字典的值"
print("SUBCLASS-INST-DICT -> " + repr(q.v))
print("Q-V-TYPE -> " + type(Q.__dict__["v"]).__name__)
