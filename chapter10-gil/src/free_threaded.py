# -*- coding: utf-8 -*-
"""free-threaded 构建对拍：同一份 CPU 活，GIL 版 vs 无 GIL 版。

本机默认构建是 GIL 版（C:/Python314 里没有 python314t.exe）。
便携版 free-threaded 构建放在 D:/Agent/tmp/py-topic10/ft/（python.org 官方
python-3.14.10t-embeddable-amd64.zip，不装系统、不改 PATH），
父进程用子进程方式把同一份 bench 在「本解释器」和「ft 解释器」上各跑一遍。
找不到 ft 就如实打印「无法实测」，不编数据。

bench 内容：
  单线程：固定量的质数计算 ×2 轮取快 —— 用来量 free-threading 的「单线程性能税」
  多线程：2/4/8 线程做同样的总量 —— 用来量 thread 到底能不能加速
  竞态：4 线程 × 25 万次 x += 1 —— 用来量无 GIL 之后丢失有多严重
只 print，不写文件。
"""
import os
import pathlib
import subprocess
import sys
import threading
import time

FT_CANDIDATES = [
    os.environ.get("PYT_FT_PYTHON", ""),
    r"D:/Agent/tmp/py-topic10/ft/python3.14t.exe",
    r"D:/Agent/tmp/py-topic10/ft/python.exe",
]

CHUNKS = 8
SPAN = 60_000
BASE = 2
RACE_THREADS = 4
RACE_PER = 250_000

X = 0


def count_primes(lo, hi):
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


def single_run():
    t0 = time.perf_counter()
    total = 0
    for i in range(CHUNKS):
        total += count_primes(BASE + i * SPAN, BASE + (i + 1) * SPAN)
    return total, time.perf_counter() - t0


def thread_run(n):
    """n 个线程分担 CHUNKS 份活（每份都数完，总量与单线程一致）。"""
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
            results[i] = count_primes(BASE + i * SPAN, BASE + (i + 1) * SPAN)

    ths = [threading.Thread(target=worker) for _ in range(n)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    return sum(results), time.perf_counter() - t0


def race_run():
    global X
    X = 0

    def bump(per):
        global X
        for _ in range(per):
            X += 1

    ths = [threading.Thread(target=bump, args=(RACE_PER,)) for _ in range(RACE_THREADS)]
    for t in ths: t.start()
    for t in ths: t.join()
    return X, RACE_THREADS * RACE_PER


def bench():
    is_gil = getattr(sys, "_is_gil_enabled", None)
    print("CBENCH_VER\t%s" % sys.version.replace("\n", " "))
    print("CBENCH_EXE\t%s" % sys.executable)
    print("CBENCH_GIL\t%s" % (is_gil() if is_gil else "无接口"))
    print("CBENCH_SWITCH\t%.4f" % sys.getswitchinterval())

    t_single = min(single_run()[1] for _ in range(2))
    print("CBENCH_SINGLE\t%.3f" % t_single)
    for n in (2, 4, 8):
        t = min(thread_run(n)[1] for _ in range(2))
        print("CBENCH_THREAD\t%d\t%.3f" % (n, t))
    got, total = race_run()
    print("CBENCH_RACE\t%d\t%d\t%d" % (RACE_THREADS, total, total - got))


def find_ft():
    for c in FT_CANDIDATES:
        if c and pathlib.Path(c).is_file():
            return c
    return None


def run_child(exe, tag):
    try:
        r = subprocess.run([exe, "-X", "utf8", str(pathlib.Path(__file__).resolve()), "--bench"],
                           capture_output=True, text=True, errors="replace", timeout=300)
    except Exception as e:
        print("CHILD\t%s\t失败\t%s: %s" % (tag, type(e).__name__, str(e)[:100]))
        return None
    if r.returncode != 0:
        tail = (r.stderr or "").strip().splitlines()
        print("CHILD\t%s\t失败\trc=%d %s" % (tag, r.returncode, tail[-1] if tail else ""))
        return None
    d = {"tag": tag}
    for line in r.stdout.splitlines():
        p = line.split("\t")
        if p[0] == "CBENCH_VER":
            d["ver"] = p[1]
        elif p[0] == "CBENCH_EXE":
            d["exe"] = p[1]
        elif p[0] == "CBENCH_GIL":
            d["gil"] = p[1]
        elif p[0] == "CBENCH_SWITCH":
            d["switch"] = float(p[1])
        elif p[0] == "CBENCH_SINGLE":
            d["single"] = float(p[1])
        elif p[0] == "CBENCH_THREAD":
            d.setdefault("threads", {})[int(p[1])] = float(p[2])
        elif p[0] == "CBENCH_RACE":
            d["race_n"] = int(p[1])
            d["race_total"] = int(p[2])
            d["race_lost"] = int(p[3])
    return d


def main():
    if "--bench" in sys.argv:
        bench()
        return

    print("VERSION\t%s\t%s" % (sys.version.split()[0], sys.executable))
    print("PLAN\t单线程 %d 份质数计算 ×2 轮取快；2/4/8 线程同总量；竞态 %d 线程 × %d 次"
          % (CHUNKS, RACE_THREADS, RACE_PER))

    rows = []
    me = sys.executable
    d = run_child(me, "本解释器")
    if d:
        rows.append(d)
    ft = find_ft()
    if ft:
        print("FT_FOUND\t%s" % ft)
        d = run_child(ft, "free-threaded")
        if d:
            rows.append(d)
    else:
        print("FT_FOUND\t没找到便携版 free-threaded 构建（无法实测，只能文档记载）")

    if not rows:
        print("RESULT\t子进程全部失败，本探针没有可用数据")
        return

    for d in rows:
        base = d.get("single", 0)
        print("BUILD\t%s\t%s\tGIL=%s\t单线程 %.3f s\t线程切换 %.2f ms"
              % (d["tag"], d.get("ver", "?"), d.get("gil", "?"), base, d.get("switch", 0) * 1000))
        for n, t in sorted(d.get("threads", {}).items()):
            speed = base / t if t else 0        # 总量固定，加速比 = 单线程 ÷ n 线程
            print("BUILD_THREAD\t%s\t%d\t%.3f\t%.2f" % (d["tag"], n, t, speed))
        if "race_lost" in d:
            print("BUILD_RACE\t%s\t%d\t%d\t%.2f%%"
                  % (d["tag"], d["race_lost"], d["race_total"],
                     d["race_lost"] * 100.0 / d["race_total"]))

    if len(rows) == 2:
        a, b = rows
        if a.get("single") and b.get("single"):
            tax = b["single"] / a["single"]
            print("TAX\t单线程性能：ft ÷ 本解释器 = %.2f（%.3f s vs %.3f s）"
                  % (tax, b["single"], a["single"]))
        sa = a["single"] / a["threads"][4] if a.get("threads", {}).get(4) else 0
        sb = b["single"] / b["threads"][4] if b.get("threads", {}).get(4) else 0
        print("SCALE\t4 线程加速比：本解释器 %.2f× / ft %.2f×" % (sa, sb))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
