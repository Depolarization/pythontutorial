"""引用计数：getrefcount 的 +1 偏移，以及「del 即回收、不等 GC」的即时性。
纯标准库，只 print 不写文件；GC 关闭状态也做对照——引用计数不依赖分代 GC。"""
import gc
import sys

print("PY " + ".".join(map(str, sys.version_info[:3])))

# == 1. getrefcount 的 +1 偏移 ==
fresh = object()                       # 全局名 fresh 是它此刻唯一的引用
print("REF fresh 仅1个引用 -> getrefcount=%d，真计数=%d"
      % (sys.getrefcount(fresh), sys.getrefcount(fresh) - 1))
h1 = [fresh]                           # +1 个列表槽位引用
print("REF 挂进1个列表   -> getrefcount=%d" % sys.getrefcount(fresh))
h2 = [fresh] * 4                       # +4 个槽位引用
print("REF 再挂4个槽位   -> getrefcount=%d" % sys.getrefcount(fresh))
del h1, h2
print("REF 别名删光      -> getrefcount=%d（回到真计数 1 + 偏移 1）"
      % sys.getrefcount(fresh))
print("OFFSET 偏移       -> 恒为 +1（传入 getrefcount 的临时参数引用）")

# == 2. 即时释放：函数返回，对象当场死（GC 关闭也照样） ==
class Noisy:
    def __init__(self, tag):
        self.tag = tag

    def __del__(self):
        print("DEL  <%s> 引用归零，立刻回收" % self.tag)


def live_briefly(tag):
    o = Noisy(tag)
    print("ALIVE <%s> 还在函数里" % tag)
    return "returned"


gc.disable()                           # 关掉 GC：回收不能赖在 GC 头上
print("GCOFF GC 状态 -> %s（已手动关闭）" % ("enabled" if gc.isenabled() else "disabled"))
r = live_briefly("局部对象")           # 函数返回 → 局部名没了 → 计数归零 → 立刻 DEL
print("CALL  函数已返回 -> %s（上一行应是 DEL）" % r)

o = Noisy("del对象")
print("DELCALL o 已创建，马上执行 del o")
del o                                  # del 的本质是删名 → 计数归零 → 立刻 DEL
print("DELCALL del 执行完毕（上一行应是 DEL）")
gc.enable()
print("GCON  GC 恢复 -> %s" % ("enabled" if gc.isenabled() else "disabled"))
