# -*- coding: utf-8 -*-
"""I/O 密集负载：本地文件 I/O + 回环 TCP，serial / 线程 / asyncio 三方对比。

外部网络这台机器不可控（探针会先试一次并如实打印），所以两种负载都落在本机：
  1) FILE 本地文件 I/O：160 个 4KB 小文件，每个请求读一次，外加 4ms 模拟延迟
     （真实磁盘/网络 RTT 就是这一量级，探针把它显式写出来，不装作是零延迟）
  2) SOCK 回环 TCP（127.0.0.1）：一个 asyncio 回声服务器，服务端每次等 4ms 再回包
     —— 这是纯粹的「等 I/O」，CPU 几乎不干活
临时文件只落在 D:/Agent/tmp/py-topic10 下，跑完删干净；只 print。
"""
import asyncio
import os
import pathlib
import shutil
import socket
import sys
import tempfile
import threading
import time

DELAY = 0.004          # 每次 I/O 的等待时间（秒）
REQS = 160             # 请求数
THREADS = 8            # 线程数
NET_HOST = ("www.python.org", 443)


# ---------------- 负载 1：本地文件 I/O ----------------
def make_files(base, n, size=4096):
    d = pathlib.Path(base)
    for i in range(n):
        (d / ("f%03d.bin" % i)).write_bytes(b"x" * size)
    return [str(d / ("f%03d.bin" % i)) for i in range(n)]


def fetch_file(path):
    with open(path, "rb") as f:
        data = f.read()
    time.sleep(DELAY)                 # 模拟真实 I/O 的等待（磁盘寻道 / 网络 RTT）
    return len(data)


def run_serial_file(paths):
    t0 = time.perf_counter()
    total = sum(fetch_file(p) for p in paths)
    return total, time.perf_counter() - t0


def run_thread_file(paths, n=THREADS):
    lock = threading.Lock()
    pos = [0]
    total = [0]

    def worker():
        while True:
            with lock:
                i = pos[0]
                if i >= len(paths):
                    return
                pos[0] = i + 1
            got = fetch_file(paths[i])
            with lock:
                total[0] += got

    ths = [threading.Thread(target=worker) for _ in range(n)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    return total[0], time.perf_counter() - t0


async def run_async_file(paths, n=THREADS):
    """标准库没有异步文件 API：asyncio 读文件只能 to_thread —— 也就是回到线程池。"""
    total = 0
    t0 = time.perf_counter()
    for i in range(0, len(paths), n):
        batch = paths[i:i + n]
        got = await asyncio.gather(*(asyncio.to_thread(fetch_file, p) for p in batch))
        total += sum(got)
    return total, time.perf_counter() - t0


# ---------------- 负载 2：回环 TCP ----------------
class EchoServer:
    """asyncio 回声服务器，跑在后台线程里；每次回包前等 DELAY 秒。"""

    def __init__(self, delay=DELAY):
        self.delay = delay
        self.port = None
        self.loop = None
        self._ready = threading.Event()
        self._stop = None
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()
        if not self._ready.wait(10):
            raise RuntimeError("回环服务器没起来")
        return self

    def _run(self):
        asyncio.run(self._serve())

    async def _serve(self):
        self.loop = asyncio.get_running_loop()
        self._stop = asyncio.Event()
        srv = await asyncio.start_server(self._handle, "127.0.0.1", 0)
        self.port = srv.sockets[0].getsockname()[1]
        self._ready.set()
        await self._stop.wait()
        srv.close()
        await srv.wait_closed()

    async def _handle(self, reader, writer):
        try:
            data = await reader.read(64)
            await asyncio.sleep(self.delay)          # 服务端的「查库 / 等上游」
            writer.write(data)
            await writer.drain()
        except Exception:
            pass
        finally:
            try:
                writer.close()
            except Exception:
                pass

    def close(self):
        if self.loop and self._stop:
            self.loop.call_soon_threadsafe(self._stop.set)
        self._thread.join(timeout=5)


def sock_one(port):
    s = socket.create_connection(("127.0.0.1", port), timeout=5)
    try:
        s.sendall(b"ping")
        return len(s.recv(64))
    finally:
        s.close()


def run_serial_sock(port, reqs=REQS):
    t0 = time.perf_counter()
    total = sum(sock_one(port) for _ in range(reqs))
    return total, time.perf_counter() - t0


def run_thread_sock(port, reqs=REQS, n=THREADS):
    total = [0]
    lock = threading.Lock()

    def worker(k):
        got = 0
        for _ in range(k):
            got += sock_one(port)
        with lock:
            total[0] += got

    per = reqs // n
    ths = [threading.Thread(target=worker, args=(per,)) for _ in range(n)]
    t0 = time.perf_counter()
    for t in ths: t.start()
    for t in ths: t.join()
    return total[0], time.perf_counter() - t0


async def run_async_sock(port, reqs=REQS):
    async def one():
        reader, writer = await asyncio.open_connection("127.0.0.1", port)
        try:
            writer.write(b"ping")
            await writer.drain()
            data = await reader.read(64)
            return len(data)
        finally:
            writer.close()

    t0 = time.perf_counter()
    got = await asyncio.gather(*(one() for _ in range(reqs)))
    return sum(got), time.perf_counter() - t0


def net_check():
    """外部网络能不能连？探针只报事实，不据此改结论。"""
    t0 = time.perf_counter()
    try:
        s = socket.create_connection(NET_HOST, timeout=2.0)
        s.close()
        return "可达", (time.perf_counter() - t0) * 1000
    except Exception as e:
        return "不可达(%s)" % type(e).__name__, (time.perf_counter() - t0) * 1000


def main():
    print("VERSION\t%s\t%s" % (sys.version.split()[0], sys.executable))
    print("PLAN\t每请求 %.1f ms 模拟 I/O 等待，共 %d 个请求，线程数 %d"
          % (DELAY * 1000, REQS, THREADS))
    state, ms = net_check()
    print("NET\t外部网络 %s:443 %s（%.0f ms）—— 本探针不依赖它" % (NET_HOST[0], state, ms))

    base = pathlib.Path(r"D:/Agent/tmp/py-topic10")
    base.mkdir(parents=True, exist_ok=True)
    work = tempfile.mkdtemp(prefix="io_", dir=str(base))
    server = None
    try:
        paths = make_files(work, REQS)
        got, el = run_serial_file(paths)
        base_file = el
        print("FILE\tserial\t1\t%.3f\t1.00\t%d" % (el, got))
        got, el = run_thread_file(paths)
        print("FILE\tthread\t%d\t%.3f\t%.2f\t%d" % (THREADS, el, base_file / el, got))
        got, el = asyncio.run(run_async_file(paths))
        print("FILE\tasyncio\t%d\t%.3f\t%.2f\t%d" % (THREADS, el, base_file / el, got))

        server = EchoServer().start()
        print("SOCK\tport\t%d\t%.3f\t%.2f\t%d" % (server.port, 0.0, 0.0, 0))
        got, el = run_serial_sock(server.port)
        base_sock = el
        print("SOCK\tserial\t1\t%.3f\t1.00\t%d" % (el, got))
        got, el = run_thread_sock(server.port)
        print("SOCK\tthread\t%d\t%.3f\t%.2f\t%d" % (THREADS, el, base_sock / el, got))
        got, el = asyncio.run(run_async_sock(server.port))
        print("SOCK\tasyncio\t%d\t%.3f\t%.2f\t%d" % (REQS, el, base_sock / el, got))
    finally:
        if server:
            server.close()
        shutil.rmtree(work, ignore_errors=True)
    print("CLEAN\t临时目录已删除：%s" % work)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
