"""惰性求值的内存账：100 万元素，列表 vs 生成器表达式 vs itertools.tee。

getsizeof 只量容器自己那一层（不含元素对象）；tracemalloc 量真实分配，
更接近账单。四个场景用 reset_peak 切开，互不污染。
"""
import gc
import sys
import tracemalloc
from itertools import tee

N = 1000000
print("PY " + ".".join(map(str, sys.version_info[:3])))


# == 1. getsizeof：容器自身的账单 ==
lst = [x for x in range(N)]
gen = (x for x in range(N))
size_l = sys.getsizeof(lst)
size_g = sys.getsizeof(gen)
print("SIZEOF list(100万元素) -> %d 字节" % size_l)
print("SIZEOF genexpr         -> %d 字节" % size_g)
print("SIZEOF RATIO           -> %.0f 倍" % (size_l / size_g))
del lst, gen
gc.collect()

# == 2. tracemalloc 峰值：真账单 ==
tracemalloc.start()
lst = [x for x in range(N)]          # 100 万个 int 对象 + 容器，一次全建
cur, peak = tracemalloc.get_traced_memory()
print("TRACE list    -> 当前 %d / 峰值 %d" % (cur, peak))
del lst
gc.collect()
tracemalloc.reset_peak()
cur, peak = tracemalloc.get_traced_memory()
print("TRACE 清场    -> 当前 %d / 峰值 %d（归零证据）" % (cur, peak))
gen = (x for x in range(N))          # 生成器：建壳不建元素
total = sum(gen)
cur, peak = tracemalloc.get_traced_memory()
print("TRACE genexpr -> sum=%d 当前 %d / 峰值 %d" % (total, cur, peak))
del gen
gc.collect()
tracemalloc.reset_peak()

# == 3. itertools.tee：两个副本，一条缓存 ==
src = (x for x in range(N))
a, b = tee(src)
head_b = next(b)                     # b 只走一步
sum_a = sum(a)                       # a 一口气走完 100 万
cur, peak = tracemalloc.get_traced_memory()
print("TEE lazy      -> b只走1步 head=%d sum_a=%d 当前 %d / 峰值 %d" % (head_b, sum_a, cur, peak))
del a, b, src
gc.collect()
tracemalloc.reset_peak()

# == 4. 对照组：同一件事拆两次独立迭代 ==
s1 = sum(x for x in range(N))
s2 = sum(x for x in range(N))
cur, peak = tracemalloc.get_traced_memory()
print("TRACE 独立两次 -> %d + %d 当前 %d / 峰值 %d" % (s1, s2, cur, peak))
tracemalloc.stop()
