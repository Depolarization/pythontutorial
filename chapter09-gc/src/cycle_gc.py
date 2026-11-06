"""循环引用：双向成环的对象引用计数永不归零，只有分代 GC 能收。
开关 GC 各跑 10 万次节点创建，用 gc 统计对拍；再上 DEBUG_SAVEALL 抓不可达对象。"""
import gc
import sys
import time

print("PY " + ".".join(map(str, sys.version_info[:3])))


class Node:
    __slots__ = ("peer",)

    def __init__(self):
        self.peer = None


def build(n):
    """造 n 对双向环节点，随后引用全部丢弃：计数互相拉扯，永远不会归零。"""
    for _ in range(n):
        a = Node()
        b = Node()
        a.peer = b
        b.peer = a


N = 100000

# == 1. GC 开着：环在 gen0 就被收走 ==
st0 = [s["collections"] for s in gc.get_stats()]
t0 = time.perf_counter()
build(N)
elapsed_on = time.perf_counter() - t0
st1 = [s["collections"] for s in gc.get_stats()]
left = gc.collect()
print("GCON   10 万次双向环创建 -> 耗时 %.3f s" % elapsed_on)
print("GCON   期间自动回收 gen0=%d gen1=%d gen2=%d 次"
      % (st1[0] - st0[0], st1[1] - st0[1], st1[2] - st0[2]))
print("GCON   收尾 gc.collect() -> 只剩 %d 个漏网" % left)

# == 2. GC 关掉：环全部堆积，只有手动 collect 能收 ==
gc.disable()
st0 = [s["collections"] for s in gc.get_stats()]
t0 = time.perf_counter()
build(N)
elapsed_off = time.perf_counter() - t0
st1 = [s["collections"] for s in gc.get_stats()]
print("GCOFF  10 万次双向环创建 -> 耗时 %.3f s" % elapsed_off)
print("GCOFF  期间自动回收 gen0=%d 次（一次都没跑）" % (st1[0] - st0[0]))
print("GCOFF  gc.get_count() -> %r（gen0 计数远超阈值）" % (gc.get_count(),))
swept = gc.collect()
print("GCOFF  手动 gc.collect() -> 收回 %d 个（≈10 万对环节点）" % swept)
gc.enable()

# == 3. DEBUG_SAVEALL：把不可达对象抓进 gc.garbage ==
class Evidence:
    def __init__(self, tag):
        self.tag = tag


gc.set_debug(gc.DEBUG_SAVEALL)
x = Evidence("环甲")
y = Evidence("环乙")
x.peer = y
y.peer = x                       # 双向环
del x, y
before = len(gc.garbage)
got = gc.collect()
caught = gc.garbage[before:]
print("SAVEALL gc.collect() -> 返回 %d，gc.garbage 增量 %d" % (got, len(caught)))
print("SAVEALL 抓到的不可达对象 -> %s"
      % [getattr(g, "tag", type(g).__name__) for g in caught])
gc.set_debug(0)
gc.garbage.clear()
gc.collect()
print("CLEAN  清理后 gc.garbage -> %d 条，DEBUG 已关" % len(gc.garbage))
