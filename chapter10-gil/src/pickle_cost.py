# -*- coding: utf-8 -*-
"""跨进程传输的账单：pickle 要多少钱。

进程池的每个参数和每个返回值都要序列化一遍（pickle），线程池不用。
这里把同一份 10 万条记录的列表，分别走三种通道，量出真实差价。
只 print，不写文件。
"""
import pickle
import sys
import time
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

N = 400_000


def build_payload(n=N):
    """10 万条「像从数据库里捞出来的」记录。"""
    return [{"id": i, "name": "user-%06d" % i, "score": (i * 37 % 1000) / 10.0} for i in range(n)]


def take_count(payload):
    """工人什么都不干，只报数——好把传输成本从计算成本里剥出来。"""
    return len(payload)


def take_int(x):
    return x + 1


def echo_if_same(payload):
    """原样把列表传回去：参数和返回值各 pickle 一遍，量「往返」的账。"""
    return payload


def timed(fn, *a):
    t0 = time.perf_counter()
    r = fn(*a)
    return r, time.perf_counter() - t0


def main():
    print("VERSION\t%s\t%s" % (sys.version.split()[0], sys.executable))
    payload = build_payload()
    print("PAYLOAD\t%d 条记录 × 3 字段" % len(payload))

    blob, el = timed(pickle.dumps, payload, pickle.HIGHEST_PROTOCOL)
    print("DUMP\t%.3f s\t%d 字节\t%.1f MB" % (el, len(blob), len(blob) / 1024 / 1024))
    back, el2 = timed(pickle.loads, blob)
    print("LOAD\t%.3f s\t%d 条" % (el2, len(back)))
    print("SIZEPER\t每条记录 %.0f 字节（pickle 后）" % (len(blob) / len(payload)))

    with ThreadPoolExecutor(max_workers=4) as tp:
        _, el_t_big = timed(tp.submit(take_count, payload).result)
        print("THREAD\t大对象\t%.4f s（同一进程内，零拷贝传引用）" % el_t_big)
        _, el_t_small = timed(tp.submit(take_int, 1).result)
        print("THREAD\t小整数\t%.4f s" % el_t_small)

    with ProcessPoolExecutor(max_workers=4) as ex:
        ex.submit(take_int, 0).result()          # 先把进程点起来，别把 spawn 算进传输时间
        _, el_p_small = timed(ex.submit(take_int, 1).result)
        print("PROC\t小整数\t%.4f s" % el_p_small)
        _, el_p_big = timed(ex.submit(take_count, payload).result)
        print("PROC\t大对象\t%.4f s（参数 pickle 一遍，返回值只回一个 len）" % el_p_big)
        _, el_p_back = timed(ex.submit(echo_if_same, payload).result)
        print("PROC\t大对象往返\t%.4f s（参数 + 返回值各 pickle 一遍）" % el_p_back)
        print("RATIO\t大对象 ÷ 小整数\t%.1f 倍" % (el_p_big / el_p_small if el_p_small else 0))

    print("CHECK\t三条通道拿到的是同一个答案：%s" % (take_count(payload) == N))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
