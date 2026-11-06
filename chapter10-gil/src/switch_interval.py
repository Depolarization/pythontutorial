# -*- coding: utf-8 -*-
"""sys.setswitchinterval：GIL 的切换粒度到底有多细。

两把尺子量同一件事：
  OBS  —— 观察者线程空转读一个全局计数器，记录「看到新值」的时间间隔中位数，
          它约等于当前设置下一次真正发生 GIL 交班的时间。
  THRU —— 8 个线程做同一份 CPU 活（对照：同样四份活串行做一遍），
          粒度调细之后切得勤了，但总时间反而更长——切换本身要钱。
只 print，不写文件。
"""
import statistics
import sys
import threading
import time

INTERVALS = [0.005, 0.001, 0.0001, 0.00001, 0.000001]   # 5ms → 1us
SAMPLE = 0.60                                            # 每个粒度的观察时长（秒）
PER = 1_250_000                                          # 每个线程的整数循环次数
NT = 8                                                   # 吞吐测试的线程数


def observe(interval, seconds=SAMPLE):
    """观察者空转读计数器，统计每次「看到变化」的间隔（毫秒）。"""
    sys.setswitchinterval(interval)
    cnt = [0]
    stop = [False]

    def worker():
        c = 0
        while not stop[0]:
            c += 1
            cnt[0] = c

    t = threading.Thread(target=worker)
    t.start()
    deltas = []
    last = cnt[0]
    ts = time.perf_counter()
    t0 = ts
    while time.perf_counter() - t0 < seconds:
        v = cnt[0]
        if v != last:
            now = time.perf_counter()
            deltas.append((now - ts) * 1000.0)
            ts = now
            last = v
    stop[0] = True
    t.join()
    d = [x for x in deltas if 0.0005 < x < 500]
    if not d:
        return -1.0, -1.0, 0
    d.sort()
    return statistics.median(d), d[int(len(d) * 0.9)], len(d)


def spin(n):
    """一份固定的 CPU 活（纯整数运算）。"""
    s = 0
    for i in range(n):
        s += (i * i) % 7
    return s


def throughput(interval, per=PER, nt=NT):
    sys.setswitchinterval(interval)
    ths = [threading.Thread(target=spin, args=(per,)) for _ in range(nt)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    return time.perf_counter() - t0


def serial_ref(per=PER, nt=NT):
    t0 = time.perf_counter()
    for _ in range(nt):
        spin(per)
    return time.perf_counter() - t0


def main():
    print("VERSION\t%s\t%s" % (sys.version.split()[0], sys.executable))
    print("DEFAULT\t默认切换间隔 %.4f ms（sys.getswitchinterval）" % (sys.getswitchinterval() * 1000))
    for iv in INTERVALS:
        med, p90, n = observe(iv)
        print("OBS\t%.6f\t%.4f\t%.4f\t%d" % (iv, med, p90, n))

    base = serial_ref()
    print("SERIAL\t同样 %d 份活串行跑 %.3f s（%d 线程的对照基准）" % (NT, base, NT))
    for iv in INTERVALS:
        el = throughput(iv)
        print("THRU\t%.6f\t%.3f\t%.2f" % (iv, el, el / base))
    sys.setswitchinterval(0.005)
    print("RESTORE\t已恢复默认 %.4f ms" % (sys.getswitchinterval() * 1000))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
