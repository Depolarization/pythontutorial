"""分代阈值与停顿：gc.get_threshold/get_stats 双解释器实测；同一负载下自动 gen0
次数随阈值不同；gc.collect() 的成本随存活对象数增长；gc.callbacks 量自动回收停顿。"""
import gc
import sys
import time

print("PY " + ".".join(map(str, sys.version_info[:3])))

# == 1. 阈值与三代计数器 ==
th = gc.get_threshold()
print("THRESHOLD gc.get_threshold() -> (%d, %d, %d)" % th)
print("COUNT   gc.get_count() -> (%d, %d, %d)" % tuple(gc.get_count()))
for g, s in enumerate(gc.get_stats()):
    print("STATS   gen%d -> collections=%d collected=%d uncollectable=%d"
          % (g, s["collections"], s["collected"], s["uncollectable"]))

# == 2. 同一负载：阈值不同，自动 gen0 次数不同 ==
base0 = gc.get_stats()[0]["collections"]
hold = []
for i in range(10000):
    hold.append([i])                   # 存活对象持续累积，只能靠 gen0 扫
auto0 = gc.get_stats()[0]["collections"] - base0
del hold
gc.collect()
print("WORK    挂 10000 个存活列表 -> 期间 gen0 自动回收 %d 次" % auto0)
print("PREDICT 预期 ≈ 10000//阈值0 = %d 次（本机阈值0=%d）" % (10000 // th[0], th[0]))

# == 3. gc.collect() 的成本：存活对象越多越贵 ==
t0 = time.perf_counter()
n0 = gc.collect()
print("COLLECT 干净堆全量       -> %.2f ms（收回 %d 个）"
      % ((time.perf_counter() - t0) * 1000, n0))
heap = [[i] for i in range(200000)]    # 20 万个存活的被追踪对象
t0 = time.perf_counter()
n1 = gc.collect()
print("COLLECT 20万存活对象全量 -> %.2f ms（收回 %d 个）"
      % ((time.perf_counter() - t0) * 1000, n1))
del heap
t0 = time.perf_counter()
n2 = gc.collect()
print("COLLECT 清掉后再全量     -> %.2f ms（收回 %d 个）"
      % ((time.perf_counter() - t0) * 1000, n2))

# == 4. gc.callbacks：量自动回收的停顿 ==
pauses = []


def probe(phase, info):
    if phase == "start":
        probe.t0 = time.perf_counter()
    else:
        pauses.append(((time.perf_counter() - probe.t0) * 1000, info["generation"]))


gc.callbacks.append(probe)
ballast = []
for i in range(60000):
    ballast.append([i, i + 1])
gc.callbacks.remove(probe)
del ballast
gc.collect()
worst = max(pauses)
print("CB      自动回收 %d 次 -> 最大停顿 %.2f ms（gen%d），累计 %.2f ms"
      % (len(pauses), worst[0], worst[1], sum(p for p, _ in pauses)))
