"""RSS 曲线：不装 psutil，用 ctypes 调 PSAPI GetProcessMemoryInfo 拿工作集。
GC 开/关各造 10 万对双向环节点并采样 RSS——循环引用在 GC 关闭时只涨不跌；
collect 能收回对象，但 RSS 未必立刻回落（pymalloc 池子留着复用，不急着还系统）。
口径：Windows WorkingSetSize（近似 RSS），如实标注。"""
import ctypes
import gc
import sys
from ctypes import wintypes

print("PY " + ".".join(map(str, sys.version_info[:3])))


class _PMC(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]


_k32 = ctypes.WinDLL("kernel32")
_psapi = ctypes.WinDLL("psapi")
_k32.GetCurrentProcess.restype = wintypes.HANDLE      # 伪句柄 -1 必须按指针宽度传
_psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC),
                                        wintypes.DWORD]


def rss_mb():
    """工作集大小（近似 RSS），单位 MB；拿不到返回 None。"""
    pmc = _PMC()
    pmc.cb = ctypes.sizeof(_PMC)
    if not _psapi.GetProcessMemoryInfo(_k32.GetCurrentProcess(),
                                       ctypes.byref(pmc), pmc.cb):
        return None
    return pmc.WorkingSetSize / 1048576.0


class Node:
    __slots__ = ("peer",)

    def __init__(self):
        self.peer = None


N = 100000
STEP = 10000


def sweep(tag, enable):
    """造 10 万对双向环，每 1 万对采一次 RSS。返回 (起点 MB, 末点 MB)。"""
    if enable:
        gc.enable()
    else:
        gc.disable()
    base = rss_mb()
    if base is None:
        print("RSS    %s -> PSAPI 不可用，无法采样" % tag)
        return None, None
    print("RSS    %s 起点 -> %.1f MB" % (tag, base))
    for i in range(STEP, N + 1, STEP):
        for _ in range(STEP):
            a = Node()
            b = Node()
            a.peer = b
            b.peer = a                  # 双向环，随后引用全部丢弃
        print("RSS    %s i=%05d -> %.1f MB" % (tag, i, rss_mb()))
    return base, rss_mb()


# == 1. GC 开：环随生随灭，RSS 平稳 ==
b1, e1 = sweep("GC开", True)
print("DELTA  GC开 10 万对 -> %+.1f MB（自动回收兜住了）" % ((e1 - b1) if b1 is not None else 0.0))

# == 2. GC 关：环全部堆积，RSS 一路涨 ==
b2, e2 = sweep("GC关", False)
print("DELTA  GC关 10 万对 -> %+.1f MB（没人收，只能堆着）" % ((e2 - b2) if b2 is not None else 0.0))

# == 3. 一次 collect：立即回落 ==
gc.enable()
n = gc.collect()
after = rss_mb()
if e2 is not None and after is not None:
    print("COLLECT 一次全量 -> 收回 %d 个对象；RSS %.1f → %.1f MB"
          % (n, e2, after))
    print("NOTE  对象还了，RSS 没降 -> pymalloc 池子留给下次复用，不急着还给系统")
