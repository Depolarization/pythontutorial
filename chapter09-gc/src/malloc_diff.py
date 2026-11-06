"""tracemalloc 快照对比：定位「内存是谁涨的」。故意埋一个只进不出的累加列表，
前后快照 diff 直接给出文件与行号；再用「修复版」跑一遍同负载做对照。"""
import os
import sys
import tracemalloc

print("PY " + ".".join(map(str, sys.version_info[:3])))

MB = 1048576.0


def frame_of(st):
    """快照统计里取 (文件名, 行号)。"""
    tr = st.traceback[0] if len(st.traceback) else None
    return os.path.basename(tr.filename), tr.lineno


# == 1. 开表，取前快照 ==
tracemalloc.start()
s1 = tracemalloc.take_snapshot()
c1, p1 = tracemalloc.get_traced_memory()
print("BASE   起始 -> current=%.2f MB peak=%.2f MB" % (c1 / MB, p1 / MB))

# == 2. 业务负载：有界缓存是正常的，累加列表是埋的泄漏 ==
CACHE = {}                       # 正常：键空间有界，覆盖写
LEAK = []                        # 泄漏点：只 append 从不清理
for i in range(50000):
    CACHE[i % 100] = ("row", i, "x" * 40)
    LEAK.append(bytes(64))       # ← 每次循环攒 64 字节
c2, p2 = tracemalloc.get_traced_memory()
print("AFTER  5 万次循环 -> current=%.2f MB（增 %+.2f MB）peak=%.2f MB"
      % (c2 / MB, (c2 - c1) / MB, p2 / MB))

# == 3. diff：按行号对比，谁在涨一目了然 ==
s2 = tracemalloc.take_snapshot()
diff = s2.compare_to(s1, "lineno")
print("TOP    增长最大的 5 处（文件:行号 -> 增量）：")
for st in diff[:5]:
    fname, lineno = frame_of(st)
    print("  %s:%d -> %+.1f KB" % (fname, lineno, st.size_diff / 1024))

# == 4. 修复对照：去掉累加列表，同样的负载几乎零增长 ==
tracemalloc.stop()
tracemalloc.start()
s1 = tracemalloc.take_snapshot()
f1, _ = tracemalloc.get_traced_memory()
CACHE = {}
for i in range(50000):
    CACHE[i % 100] = ("row", i, "x" * 40)    # 只留有界缓存
f2, _ = tracemalloc.get_traced_memory()
s2 = tracemalloc.take_snapshot()
diff = s2.compare_to(s1, "lineno")
fname, lineno = frame_of(diff[0])
print("FIXED  同负载无泄漏 -> current 增 %+.2f MB，TOP1 = %s:%d %+.1f KB"
      % ((f2 - f1) / MB, fname, lineno, diff[0].size_diff / 1024))
tracemalloc.stop()
