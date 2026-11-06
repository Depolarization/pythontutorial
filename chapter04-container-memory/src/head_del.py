"""del a[0] 为什么是 O(n)：每删一个头元素，后面全部元素整体前移一格（memmove）；
collections.deque.popleft 只动头指针，两端都是 O(1)；del a[-1]（尾部）也是 O(1) 作对照。
time.perf_counter 计时，5 轮取中位；协议统一为「删掉前一半元素」，量每刀平均成本。"""
import statistics
import sys
import time
from collections import deque

# == 1. 计时底座：perf_counter 多轮取中位 ==
def bench(fn, rounds=5):
    ts = []
    for _ in range(rounds):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts)

# == 2. 同一协议下的三种删法 ==
def del_head(n):
    a = list(range(n))
    for _ in range(n // 2):
        del a[0]                             # 每次整体前移

def pop_left(n):
    d = deque(range(n))
    for _ in range(n // 2):
        d.popleft()                          # 只动头指针

def del_tail(n):
    a = list(range(n))
    for _ in range(n // 2):
        del a[-1]                            # 尾部无需移动

# == 3. 三种规模 × 三种删法 ==
print("VERSION\t%s" % sys.version.split()[0])
print("NOTE\tdel a[0] 每次把后面全部元素前移一格（memmove）；popleft / del a[-1] 是 O(1)")
per = {}
for n in (10000, 50000, 100000):
    for name, fn in (("del a[0]", del_head), ("popleft", pop_left), ("del a[-1]", del_tail)):
        med = bench(lambda f=fn: f(n))
        per[(n, name)] = med / (n // 2) * 1e6      # 每刀平均微秒
        print("BENCH\tn=%d %-9s k=%d median=%.3fs per=%.2fus" %
              (n, name, n // 2, med, per[(n, name)]))
print("RATIO\tn=100000 每刀成本 del a[0] 是 popleft 的 %.0f 倍" %
      (per[(100000, "del a[0]")] / per[(100000, "popleft")]))
print("LINEAR\t" + "  ".join("n=%d→%.1fus" % (n, per[(n, "del a[0]")])
                             for n in (10000, 50000, 100000)) + "（规模×10 成本×10 → O(n)）")
print("FLAT\t" + "  ".join("n=%d→%.2fus" % (n, per[(n, "popleft")])
                           for n in (10000, 50000, 100000)) + "（几乎不变 → O(1)）")

# == 4. 语义自检：两种删法剩下的东西一致 ==
a = list(range(5))
d = deque(range(5))
del a[0]
d.popleft()
print("SELF-OK\t%s/2" % (2 if (a == list(d) == [1, 2, 3, 4]) else 0))
