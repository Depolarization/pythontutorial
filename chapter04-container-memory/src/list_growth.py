"""list 的超配增长：逐个 append 记录 sys.getsizeof 台阶，与 CPython 源码增长公式对拍。
3.12+ 源码公式： new_allocated = (newsize + (newsize >> 3) + 6) & ~3   （4 槽对齐）
流传的旧公式：   new_allocated = newsize + (newsize >> 3) + (3 if newsize < 9 else 6)
64 位 CPython：空 list 头部 56 字节，每槽位 8 字节。"""
import sys

# == 1. 逐个 append 记录容量台阶 ==
N = 220
a = []
steps = []                                   # (len, 容量槽位数, getsizeof 字节)
prev = base = sys.getsizeof(a)
for i in range(1, N + 1):
    a.append(i)
    s = sys.getsizeof(a)
    if s != prev:                            # 只有触发扩容的那一次会变
        steps.append((i, (s - base) // 8, s))
        prev = s

print("VERSION\t%s" % sys.version.split()[0])
print("BASE\t空 list getsizeof=%d 字节（纯头部），每槽位 8 字节" % base)
for ln, cap, b in steps:
    print("STEP\tlen=%d cap=%d bytes=%d" % (ln, cap, b))
print("LADDER\t" + ">".join(str(cap) for _, cap, _ in steps))

# == 2. 与 CPython 源码公式对拍 ==
def cap_new(n):                              # 3.12+ 源码：4 槽对齐
    return (n + (n >> 3) + 6) & ~3

def cap_old(n):                              # 3.11- 源码：文档里流传的公式
    return n + (n >> 3) + (3 if n < 9 else 6)

hit_new = hit_old = 0
for ln, cap, _ in steps:
    new, old = cap_new(ln), cap_old(ln)
    hit_new += new == cap
    hit_old += old == cap
    print("FIT\tlen=%d 实测cap=%d 新公式(3.12+)=%d 旧公式(3.11-)=%d %s" %
          (ln, cap, new, old, "新公式命中" if new == cap else "旧公式命中" if old == cap else "都不符"))
print("FIT-SUM\t共 %d 档：新公式(3.12+)命中 %d 档，旧公式(3.11-)命中 %d 档" %
      (len(steps), hit_new, hit_old))
print("SELF-OK\t%d/%d" % (hit_new, len(steps)))
