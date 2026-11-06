"""weakref 打破缓存类泄漏：普通 dict 缓存 vs weakref.WeakValueDictionary。
tracemalloc 量内存：强缓存删光外部引用后内存纹丝不动；弱缓存当场释放。"""
import gc
import sys
import tracemalloc
import weakref

print("PY " + ".".join(map(str, sys.version_info[:3])))

MB = 1048576.0


class Asset:
    def __init__(self, key):
        self.key = key
        self.blob = bytearray(512)         # 每个资源 512 字节的「有效载荷」


# == 1. 单对象：weakref 的生死观察 ==
u = Asset("单例")
r = weakref.ref(u)
print("WREF  持有强引用时 r() is u -> %s" % (r() is u))
del u                                     # 强引用没了 → 对象立刻回收（弱引用不算数）
print("WREF  del 后 r() -> %r（弱引用自动变 None）" % (r(),))

# == 2. 强引用缓存：删光外部引用，缓存里的对象照样活着 ==
tracemalloc.start()
strong = {}
keep = []
for i in range(5000):
    a = Asset(i)
    strong[i] = a
    keep.append(a)
c1 = tracemalloc.get_traced_memory()[0]
del keep
gc.collect()
c2 = tracemalloc.get_traced_memory()[0]
print("STRONG 5000 个资源进 dict 缓存 -> 在册 %.2f MB" % (c1 / MB))
print("STRONG 删光外部引用+gc 后 -> 缓存条目 %d（全还活着），在册 %.2f MB（几乎不动）"
      % (len(strong), c2 / MB))
strong.clear()
del strong
gc.collect()
c3 = tracemalloc.get_traced_memory()[0]
print("STRONG 手动清空缓存后 -> 在册 %.2f MB（这时才还）" % (c3 / MB))

# == 3. WeakValueDictionary：同样 5000 个，删光引用当场释放 ==
wd = weakref.WeakValueDictionary()
keep2 = []
for i in range(5000):
    a = Asset(i)
    wd[i] = a
    keep2.append(a)
c4 = tracemalloc.get_traced_memory()[0]
print("WEAK   5000 个资源进 WeakValueDictionary（强引用在手） -> 条目 %d，在册 %.2f MB"
      % (len(wd), c4 / MB))
del keep2
del a                                     # 别漏了循环变量手里最后一个
gc.collect()
c5 = tracemalloc.get_traced_memory()[0]
print("WEAK   删光外部引用+gc 后 -> 条目 %d，在册 %.2f MB（当场释放）"
      % (len(wd), c5 / MB))
tracemalloc.stop()
