# -*- coding: utf-8 -*-
"""GIL 保护的是解释器内部状态，不是你的数据。

七组实测（全部本机跑出来，单次测量，数值随机器负载浮动）：
  A 紧循环 x += 1，4 线程 × 25 万 = 100 万次，默认切换粒度
  B 紧循环 x += 1，16 线程 × 25 万 = 400 万次，默认切换粒度
  C 同上，切换粒度压到 1 微秒
  D 临界区里读和写之间插一次普通函数调用（现实里的校验/格式化/日志），默认粒度
  E 同上，切换粒度压到 1 微秒
  F 同上 + 锁
  G 临界区里让出 GIL（一次 I/O），转账场景
  H list.append 4 线程 × 25 万：append 本身
  I 「先查再改」+ 1 微秒粒度
  J 「先查再改」+ 锁
  K Queue 传结果
只 print，不写文件。
"""
import sys
import threading
import time
from queue import Queue

THREADS = 4
PER = 250_000                    # 4 × 25 万 = 100 万次自增
TOTAL = THREADS * PER

X = 0                            # 演示用的全局计数器
LOCK = threading.Lock()


# ---------- A~C：教科书版 x += 1 ----------
def bump_plain(per):
    global X
    for _ in range(per):
        X += 1                   # LOAD / ADD / STORE 三条字节码


def run_counter(fn, per=PER, threads=THREADS):
    global X
    X = 0
    ths = [threading.Thread(target=fn, args=(per,)) for _ in range(threads)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    return X, time.perf_counter() - t0


# ---------- D~F：读和写之间有一次函数调用 ----------
def validate(v):
    """现实代码里的「校验 / 格式化 / 记一笔日志」，这里只原样返回。"""
    return v


def bump_with_call(per):
    global X
    for _ in range(per):
        X = validate(X) + 1      # 调用点就是一个 GIL 切点，正好落在读和写中间


def bump_with_call_locked(per):
    global X
    for _ in range(per):
        with LOCK:
            X = validate(X) + 1


# ---------- G：临界区里让出 GIL（一次 I/O） ----------
BAL = [0]


def transfer(rounds):
    for _ in range(rounds):
        bal = BAL[0]             # 读余额
        time.sleep(0)            # 现实里的「查库 / 写日志 / 发通知」，这里让出 GIL
        BAL[0] = bal - 1         # 写回


# ---------- H~K：list 的诱惑 ----------
def appender(n, lst):
    for i in range(n):
        lst.append(i)            # 单条字节码，看起来「原子」


POOL = 1_000                     # 只允许 1000 个不同的值
DEDUP_THREADS = 8
DEDUP_ROUNDS = 125_000           # 8 × 12.5 万 = 100 万次「先查再改」


def dedup_plain(rounds, seen):
    for i in range(rounds):
        v = i % POOL
        if v not in seen:            # 查
            seen.append(validate(v))  # 调用 + 改：查完到写入之间被切走


def dedup_locked(rounds, seen, lk):
    for i in range(rounds):
        v = i % POOL
        with lk:
            if v not in seen:
                seen.append(validate(v))


def producer(n, q):
    for i in range(n):
        q.put(i)


def with_interval(interval, fn):
    old = sys.getswitchinterval()
    sys.setswitchinterval(interval)
    try:
        return fn()
    finally:
        sys.setswitchinterval(old)


def main():
    ver = sys.version.split()[0]
    print("VERSION\t%s\t%s" % (ver, sys.executable))
    print("SWITCH\t默认切换间隔 %.4f ms" % (sys.getswitchinterval() * 1000))
    print("PLAN\t%d 线程 × %d 次 = %d 次自增" % (THREADS, PER, TOTAL))
    is_gil = getattr(sys, "_is_gil_enabled", None)
    print("GIL\t_is_gil_enabled=%s" % (is_gil() if is_gil else "无此接口"))

    got, el = run_counter(bump_plain)
    print("A 紧循环默认粒度\t%d 次\t丢失 %d 次\t耗时 %.3f s" % (TOTAL, TOTAL - got, el))

    n16 = 16 * PER
    got, el = run_counter(bump_plain, threads=16)
    print("B 16线程默认粒度\t%d 次\t丢失 %d 次\t耗时 %.3f s" % (n16, n16 - got, el))

    got, el = with_interval(1e-6, lambda: run_counter(bump_plain))
    print("C 紧循环1us粒度\t%d 次\t丢失 %d 次\t耗时 %.3f s" % (TOTAL, TOTAL - got, el))

    got, el = run_counter(bump_with_call)
    print("D 读改写间有调用\t%d 次\t丢失 %d 次\t耗时 %.3f s" % (TOTAL, TOTAL - got, el))

    got, el = with_interval(1e-6, lambda: run_counter(bump_with_call))
    lost_e, el_e = TOTAL - got, el
    print("E 调用+1us粒度\t%d 次\t丢失 %d 次\t耗时 %.3f s" % (TOTAL, lost_e, el_e))
    print("E 丢失率\t%.2f%%" % (lost_e * 100.0 / TOTAL))

    got, el = with_interval(1e-6, lambda: run_counter(bump_with_call_locked))
    print("F 调用+1us+锁\t%d 次\t丢失 %d 次\t耗时 %.3f s" % (TOTAL, TOTAL - got, el))
    print("F 锁的代价\t%.2f 倍（同条件对比 E 段无锁）" % (el / el_e if el_e else 0))

    BAL[0] = 100_000
    rounds = 20_000
    ths = [threading.Thread(target=transfer, args=(rounds,)) for _ in range(THREADS)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    el = time.perf_counter() - t0
    print("G 临界区让出GIL\t应减 %d\t实减 %d\t丢失 %d 次\t耗时 %.3f s"
          % (THREADS * rounds, 100_000 - BAL[0], THREADS * rounds - (100_000 - BAL[0]), el))

    lst = []
    ths = [threading.Thread(target=appender, args=(PER, lst)) for _ in range(THREADS)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    el = time.perf_counter() - t0
    print("H append本身\t%d 次\t实得 %d 个\t丢失 %d 个\t耗时 %.3f s"
          % (TOTAL, len(lst), TOTAL - len(lst), el))

    seen = []

    def run_dedup(fn, *extra):
        ths = [threading.Thread(target=fn, args=(DEDUP_ROUNDS, seen) + extra)
               for _ in range(DEDUP_THREADS)]
        t0 = time.perf_counter()
        for t in ths: t.start()
        for t in ths: t.join()
        return time.perf_counter() - t0

    el = with_interval(1e-6, lambda: run_dedup(dedup_plain))
    print("I 先查再改1us\t应有 %d 个\t实得 %d 个\t多出 %d 个\t耗时 %.3f s"
          % (POOL, len(seen), len(seen) - POOL, el))

    seen2 = []
    lk = threading.Lock()
    ths = [threading.Thread(target=dedup_locked, args=(DEDUP_ROUNDS, seen2, lk))
           for _ in range(DEDUP_THREADS)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    el = time.perf_counter() - t0
    print("J 先查再改+锁\t应有 %d 个\t实得 %d 个\t多出 %d 个\t耗时 %.3f s"
          % (POOL, len(seen2), len(seen2) - POOL, el))

    q = Queue()
    ths = [threading.Thread(target=producer, args=(PER, q)) for _ in range(THREADS)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    el = time.perf_counter() - t0
    print("K Queue\t%d 次\t实得 %d 个\t丢失 %d 个\t耗时 %.3f s"
          % (TOTAL, q.qsize(), TOTAL - q.qsize(), el))

    print("结论\tGIL 的切点只在循环回跳 / 调用处，恰好避开 += 的读改写；"
          "换成 free-threaded 或让出 GIL，丢失立刻出现")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
