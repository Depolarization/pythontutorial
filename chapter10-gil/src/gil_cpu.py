# -*- coding: utf-8 -*-
"""CPU 密集负载：同一份质数计算，serial / 1~8 线程 / 2~8 进程 吞吐对比。

工作总量固定 = CHUNKS 个区间，每种配置都必须数完这些区间，才能横向比。
九种配置轮流跑 ROUNDS 轮，每种取最快的一轮：这台机器频率会漂移，
把某一种配置放在最后跑，它能凭 20% 的漂移假装自己变快了。
进程池的「启动」单独计时（Windows spawn 一个池要几百毫秒，那是另一笔账）。
Windows 上 multiprocessing 默认 spawn：子进程会重新 import 本脚本，
所以进程池只在 if __name__ == "__main__" 里创建（spawn 子进程里 __name__ 是 __mp_main__）。
只 print，不写文件。
"""
import os
import sys
import time
import threading
from concurrent.futures import ProcessPoolExecutor

CHUNKS = 8
SPAN = 60_000                    # 每个区间的宽度
BASE = 2
ROUNDS = 3

WORK = [(BASE + i * SPAN, BASE + (i + 1) * SPAN) for i in range(CHUNKS)]


def count_primes(lo, hi):
    """朴素试除法数 [lo, hi) 里的质数个数。纯 Python 循环，典型 CPU 密集。"""
    c = 0
    for n in range(lo, hi):
        if n < 2:
            continue
        d = 2
        is_prime = True
        while d * d <= n:
            if n % d == 0:
                is_prime = False
                break
            d += 1
        if is_prime:
            c += 1
    return c


def work_one(idx):
    lo, hi = WORK[idx]
    return count_primes(lo, hi)


def run_serial(_n=1):
    t0 = time.perf_counter()
    total = sum(work_one(i) for i in range(CHUNKS))
    return total, time.perf_counter() - t0, 0.0


def run_threads(n):
    results = [0] * CHUNKS
    lock = threading.Lock()
    nxt = [0]

    def worker():
        while True:
            with lock:
                i = nxt[0]
                if i >= CHUNKS:
                    return
                nxt[0] = i + 1
            results[i] = work_one(i)

    ths = [threading.Thread(target=worker) for _ in range(n)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    return sum(results), time.perf_counter() - t0, 0.0


def run_procs(n):
    ex = ProcessPoolExecutor(max_workers=n)
    try:
        t0 = time.perf_counter()
        ex.submit(abs, -1).result()             # 先空跑一个任务：把 spawn 的进程全部点起来
        startup = time.perf_counter() - t0
        t1 = time.perf_counter()
        total = sum(ex.map(work_one, range(CHUNKS)))
        work = time.perf_counter() - t1
    finally:
        ex.shutdown(wait=True)
    return total, work, startup


def main():
    print("VERSION\t%s\t%s" % (sys.version.split()[0], sys.executable))
    print("CORES\tos.cpu_count()=%d" % (os.cpu_count(),))
    print("WORKLOAD\t%d 个区间 × %d 宽 = 数到 %d；每种配置跑 %d 轮取最快"
          % (CHUNKS, SPAN, WORK[-1][1], ROUNDS))

    cfgs = [("serial", 1, run_serial)]
    cfgs += [("thread", n, (lambda n=n: run_threads(n))) for n in (1, 2, 4, 8)]
    cfgs += [("proc", n, (lambda n=n: run_procs(n))) for n in (2, 4, 8)]

    best = {}
    startup_seen = {}
    counts = {}
    for r in range(ROUNDS):
        for kind, n, fn in cfgs:
            got, el, st = fn()
            key = (kind, n)
            if el < best.get(key, 1e9):
                best[key] = el
                startup_seen[key] = st
            counts[key] = got

    base = best[("serial", 1)]
    print("CFG\tserial\t1\t%.3f\t1.00\t%d\t0.000" % (base, counts[("serial", 1)]))
    for kind in ("thread", "proc"):
        for n in ([1, 2, 4, 8] if kind == "thread" else [2, 4, 8]):
            key = (kind, n)
            print("CFG\t%s\t%d\t%.3f\t%.2f\t%d\t%.3f"
                  % (kind, n, best[key], base / best[key], counts[key], startup_seen[key]))

    same = len(set(counts.values())) == 1
    print("CHECK\t九种配置数出的质数总数是否相同：%s" % ("是" if same else "否"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
