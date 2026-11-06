"""dict 的插入顺序（3.7+ 语言规范保证）与紧凑布局证据：
插入序=遍历序；重赋值不动位；删除重插挪末尾；keys()/values() 是同源动态视图；
实例 __dict__ 走分裂表（键表共享、只存值）—— tracemalloc 实测省内存；
dict 本体按 2/3 负载率翻倍扩容的台阶。"""
import sys
import tracemalloc

# == 1. 插入顺序：与写入顺序一致，与哈希值无关 ==
d = {}
for k in (7, 3, 9, 1, 5):
    d[k] = k * 10
print("VERSION\t%s" % sys.version.split()[0])
print("INS\tint 键按 7,3,9,1,5 插入 → list(d)=%s（与插入一致，与哈希值无关）" % list(d))
ds = {}
for k in ("durian", "apple", "cherry"):
    ds[k] = 1
print("STRINS\tstr 键按 durian,apple,cherry 插入 → %s" % list(ds))

# == 2. 顺序的三个边界：重赋值 / 删除重插 ==
for k in (5, 1, 9, 3, 7):
    d[k] = -1                                  # 只改值，不动位
reassign_ok = list(d) == [7, 3, 9, 1, 5]
print("REASSIGN\t已有键倒序重赋值 → 顺序不变 %s（%s）" % (list(d), reassign_ok))
del d[9]
d[9] = -9
delreins_ok = list(d) == [7, 3, 1, 5, 9]
print("DELREINS\tdel 9 再重插 → 挪到末尾 %s（%s）" % (list(d), delreins_ok))

# == 3. keys()/values()：动态视图，键值同源同序 ==
ks = d.keys()
n0 = len(ks)
d["zz"] = 0
view_ok = len(ks) == n0 + 1 and "zz" in ks
print("VIEW\tkeys() 是活的视图：len %d→%d，'zz' in ks=%s，不复制数据" %
      (n0, len(ks), "zz" in ks))
align_ok = all(d[k] == v for k, v in zip(list(d.keys()), list(d.values())))
print("ALIGN\tkeys() 与 values() 逐位配对全部命中=%s（键集与值集来自同一份紧凑 entries）" % align_ok)

# == 4. 分裂表证据：实例 __dict__ 共享键表，只存值 ==
class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

N = 20000
tracemalloc.start()
ps = [Point(i, i + 1, i + 2) for i in range(N)]
_, pk = tracemalloc.get_traced_memory()
tracemalloc.stop()
tracemalloc.start()
ds2 = [{"x": i, "y": i + 1, "z": i + 2} for i in range(N)]
_, dk = tracemalloc.get_traced_memory()
tracemalloc.stop()
print("SPLIT\t实例 __dict__（分裂表·共享键）: %d 实例 ×3 属性 = %.2f MB，每摊 %d 字节" %
      (N, pk / 1e6, pk // N))
print("SPLIT\t独立 dict 对照: %d 个 3 键 dict = %.2f MB，每摊 %d 字节" % (N, dk / 1e6, dk // N))
print("SPLIT\t键表共享只存值 → 省 %.0f%%" % ((1 - pk / dk) * 100))

# == 5. dict 本体的扩容台阶（2/3 负载率，翻倍） ==
for n in (0, 1, 5, 6, 10, 11, 21, 22, 42, 43, 85, 86):
    print("DSTEP\tn=%d bytes=%d" % (n, sys.getsizeof({i: i for i in range(n)})))
print("SELF-OK\t%d/3" % (reassign_ok + delreins_ok + (view_ok and align_ok)))
