"""sys.modules 缓存与 from-import 的取物时机。
import 语句第一步查 sys.modules 字典；from-import 在 import 那一刻按名取一次物。"""
import sys
import _cache_counter

# == 1. import 两次，模块体只执行一次
import _cache_demo                     # 第一次：模块体真的执行
import _cache_demo as again            # 第二次：缓存命中，直接返回
print("EXEC-AFTER-FIRST -> %d" % _cache_counter.N)
print("EXEC-AFTER-SECOND -> %d" % _cache_counter.N)
print("SAME-OBJ -> %s" % (again is _cache_demo))
print("IN-SYSMODULES -> %s" % ("_cache_demo" in sys.modules))

# == 2. from-import 的取物时机：import 那一刻按名取一次物
from _cache_demo import VALUE          # 此刻 VALUE = "v1"
_cache_demo.VALUE = "v2"               # 模块属性后来被改
print("CAPTURED -> %s" % VALUE)         # 手里的旧引用：还是 v1
print("MODULE-ATTR-NOW -> %s" % _cache_demo.VALUE)
from _cache_demo import VALUE as refetch
print("REFETCH -> %s" % refetch)        # 重新 from-import 才拿到 v2

# == 3. 删掉缓存条目：下一次 import 重新执行模块体
old = sys.modules.pop("_cache_demo")
import _cache_demo as reborn
print("EXEC-AFTER-DEL -> %d" % _cache_counter.N)
print("REBORN-IS-OLD -> %s" % (reborn is old))
print("REBORN-VALUE -> %s" % reborn.VALUE)
