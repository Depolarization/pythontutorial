"""拷贝语义边界：a[:] / list(a) / copy.copy / copy.deepcopy 四种写法 × 三道检验。
浅拷贝（前三种）只换最外层容器，内层对象 identity 原样保留；
deepcopy 递归复制整棵树。矩阵：通过拷贝改内层，看原始结构跟不跟着变。"""
import copy
import sys

def fresh():
    return [[1, 2], {"x": 0}, "hello"]

# == 1. 四种拷贝：外壳与内层的 identity ==
WAYS = [("a[:]", lambda a: a[:]),
        ("list(a)", lambda a: list(a)),
        ("copy.copy", lambda a: copy.copy(a)),
        ("copy.deepcopy", lambda a: copy.deepcopy(a))]
print("VERSION\t%s" % sys.version.split()[0])
print("STRUCT\t原始 = %r" % fresh())
shallow_ok = deep_ok = 0
for name, fn in WAYS:
    a = fresh()
    c = fn(a)                                    # 同一棵树的拷贝
    outer, slist, sdict = c is not a, c[0] is a[0], c[1] is a[1]
    print("COPY\t%-13s 新外壳=%s 内层list同对象=%s 内层dict同对象=%s" %
          (name, outer, slist, sdict))
    if name == "copy.deepcopy":
        deep_ok = outer and not slist and not sdict
    else:
        shallow_ok += outer and slist and sdict

# == 2. 改内层矩阵：谁跟着变（每次用全新原始结构） ==
print("NOTE\t每次全新原始结构：通过拷贝给内层 list 追加、给内层 dict 改值，再看原始是否被牵连")
mut_ok = 0
for name, fn in WAYS:
    a = fresh()
    c = fn(a)                                    # 同一棵树的拷贝
    c[0].append(9)                              # 改内层 list
    c[1]["x"] = 99                              # 改内层 dict
    lst, dct = 9 in a[0], a[1]["x"] == 99
    print("MUT\t%-13s 改内层list→原始跟着变=%s  改内层dict→原始跟着变=%s" % (name, lst, dct))
    if name == "copy.deepcopy":
        mut_ok += (not lst) and (not dct)
    else:
        mut_ok += lst and dct

# == 3. 换掉整个槽位：任何拷贝都不牵连原始 ==
for name, fn in WAYS:
    a = fresh()
    c = fn(a)                                    # 同一棵树的拷贝
    c[0] = ["new"]                              # 顶层槽位放新对象
    print("REPLACE\t%-13s 把 c[0] 整个换成新 list → 原始第0槽=%r（任何拷贝都不会牵连）" %
          (name, a[0]))
print("SELF-OK\t%d/8" % (shallow_ok + deep_ok + mut_ok))
