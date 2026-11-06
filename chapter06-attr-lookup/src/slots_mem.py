# -*- coding: utf-8 -*-
"""__slots__ 的内存账：getsizeof 是个陷阱（不含 __dict__），父类不写 slots 照样有字典；
真实差距要用 tracemalloc 量。"""
import sys
import tracemalloc

print("VERSION\t" + sys.version.split()[0])


# == 1. 同样三个字段：普通类 vs slots 类
class WithDict:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class WithSlots:
    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


wd = WithDict(1, 2, 3)
ws = WithSlots(1, 2, 3)
print("GETSIZE WITH-DICT -> " + str(sys.getsizeof(wd)))
print("GETSIZE WITH-SLOTS -> " + str(sys.getsizeof(ws)))
print("GETSIZE-EQUAL -> " + str(sys.getsizeof(wd) == sys.getsizeof(ws)))
print("GETSIZE DICT-ALONE -> " + str(sys.getsizeof(wd.__dict__)))
print("COMBO WITH-DICT -> " + str(sys.getsizeof(wd) + sys.getsizeof(wd.__dict__)))
try:
    ws.w = 1
    print("SLOTS-EXTRA -> 可以加属性")
except AttributeError as e:
    print("SLOTS-EXTRA -> AttributeError: " + str(e))

# == 2. 父类没写 __slots__：子类照样有 __dict__
class BasePlain:
    pass


class ChildSlots(BasePlain):
    __slots__ = ("a",)


cs = ChildSlots()
cs.a = 1
try:
    cs.b = 2
    print("CHILD-DICT -> 可以随便加：实例有 __dict__")
except AttributeError:
    print("CHILD-DICT -> 加不上")
print("CHILD HAS-DICT -> " + str(hasattr(cs, "__dict__")))


class BaseSlots:
    __slots__ = ("x",)


class FullSlots(BaseSlots):
    __slots__ = ("y",)


fs = FullSlots()
fs.x = 1
fs.y = 2
try:
    fs.z = 3
    print("FULL-SLOTS -> 可以加属性")
except AttributeError as e:
    print("FULL-SLOTS -> AttributeError: " + str(e))
print("FULL HAS-DICT -> " + str(hasattr(fs, "__dict__")))

# == 3. tracemalloc 实账：同造 N 个实例，量每实例真实字节
N = 1000000


def trace_holder(n):
    tracemalloc.start()
    lst = [None] * n
    cur, _ = tracemalloc.get_traced_memory()
    del lst
    tracemalloc.stop()
    return cur


def trace_cls(cls, n):
    tracemalloc.start()
    lst = [cls(i, i, i) for i in range(n)]
    cur, _ = tracemalloc.get_traced_memory()
    del lst
    tracemalloc.stop()
    return cur


holder = trace_holder(N)
run_dict = trace_cls(WithDict, N)
run_slots = trace_cls(WithSlots, N)
per_dict = (run_dict - holder) / N
per_slots = (run_slots - holder) / N
print("N-INSTANCES -> " + str(N))
print("TRACE HOLDER -> " + str(holder))
print("TRACE WITH-DICT -> " + str(run_dict))
print("TRACE WITH-SLOTS -> " + str(run_slots))
print("PER-INST WITH-DICT -> " + str(per_dict))
print("PER-INST WITH-SLOTS -> " + str(per_slots))
print("SAVED PER-INST -> " + str(per_dict - per_slots))
print("SAVED RATIO -> " + str(per_dict / per_slots))
print("MILLION-SAVED -> " + str((per_dict - per_slots) * N))
