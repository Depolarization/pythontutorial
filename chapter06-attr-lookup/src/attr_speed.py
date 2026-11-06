# -*- coding: utf-8 -*-
"""同一对象五种属性访问写法的耗时：实例 dict / 类 dict / data descriptor /
non-data descriptor / slots。属性查找到底是不是瓶颈，量出来才知道。"""
import sys
import time

K = 1000000
REPS = 5


# == 1. 一个身怀五种访问路径的实验对象
class GetOnly:
    def __get__(self, obj, cls):
        return 9                    # 恒定值，和 property 的常数返回对齐


class Rich:
    cattr = 42                      # 类字典普通值

    def __init__(self):
        self.iattr = 1              # 实例字典

    @property
    def prop(self):                 # data descriptor
        return 7

    nd = GetOnly()                  # non-data descriptor


class Slot:
    __slots__ = ("x",)

    def __init__(self):
        self.x = 1


r = Rich()
s = Slot()


def bench(stmt):
    """预热后取 REPS 轮最快值，返回 ns / 次访问。"""
    for _ in range(200000):
        stmt()
    best = 1e18
    for _ in range(REPS):
        t0 = time.perf_counter()
        for _ in range(K):
            stmt()
        dt = time.perf_counter() - t0
        best = min(best, dt)
    return best / K * 1e9


print("VERSION\t" + sys.version.split()[0])
print("K -> " + str(K) + " 次/轮，取 " + str(REPS) + " 轮最快")

t_inst = bench(lambda: r.iattr)
t_cls = bench(lambda: r.cattr)
t_prop = bench(lambda: r.prop)
t_nd = bench(lambda: r.nd)
t_slot = bench(lambda: s.x)

print("SPEED INST-DICT -> " + str(t_inst))
print("SPEED CLASS-DICT -> " + str(t_cls))
print("SPEED DATA-DESC -> " + str(t_prop))
print("SPEED NONDATA-DESC -> " + str(t_nd))
print("SPEED SLOTS -> " + str(t_slot))
print("RATIO PROP-VS-INST -> " + str(t_prop / t_inst))
print("RATIO SLOTS-VS-INST -> " + str(t_slot / t_inst))
print("MILLION-PROP-MS -> " + str(t_prop))   # 100 万次 × ns/次 = ns×10⁶，恰即毫秒数
