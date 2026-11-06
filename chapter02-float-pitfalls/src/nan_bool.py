"""nan != nan 但 nan in [nan] 为 True（成员判断有 identity 短路）；True == 1 的 bool 继承。
纯标准库，只 print。"""
import math

nan = float("nan")

print("== nan 的 == 与 in ==")
print("NB nan == nan -> %s" % (nan == nan))
print("NB nan != nan -> %s（IEEE 754 规定 nan 与任何值比较都是不等）" % (nan != nan))
print("NB nan is nan -> %s（同一个对象）" % (nan is nan))
print("NB nan in [nan] -> %s（成员判断先比 identity，再比 ==）" % (nan in [nan]))
n2 = float("nan")
print("NB 两个不同 nan 对象 == -> %s" % (nan == n2))
print("NB 两个不同 nan 对象 in -> %s（identity 不等、== 也 False，所以找不到）" % (n2 in [nan]))
print("NB [nan].count(nan) -> %d" % [nan].count(nan))
print("NB [nan].index(nan) -> %d" % [nan].index(nan))
print("NB [nan] == [nan] -> %s（容器比较同样走 identity 短路）" % ([nan] == [nan]))
try:
    d = {nan: "ok"}
    print("NB dict 用 nan 当键取值 -> %s（哈希表也是 identity 优先）" % d[nan])
except KeyError:
    print("NB dict 用 nan 当键取值 -> KeyError")
try:
    print("NB 换一个 nan 对象查 dict -> %s" % d[n2])
except KeyError:
    print("NB 换一个 nan 对象查 dict -> KeyError（值查不到）")
print("NB math.isnan(nan) -> %s（判 nan 唯一正解）" % math.isnan(nan))
print("NB math.nan == math.nan -> %s" % (math.nan == math.nan))

print("== True == 1：bool 是 int 的子类 ==")
print("BB isinstance(True, int) -> %s" % isinstance(True, int))
print("BB issubclass(bool, int) -> %s" % issubclass(bool, int))
print("BB bool.__mro__ -> (%s)" % ", ".join(c.__name__ for c in bool.__mro__))
print("BB True == 1 -> %s；False == 0 -> %s" % (True == 1, False == 0))
print("BB True is int(1) -> %s（值相等但对象不同：True 是 bool，1 是 int）" % (True is int(1)))
print("BB hash(True) == hash(1) -> %s" % (hash(True) == hash(1)))
print("BB {True: 'a', 1: 'b'} -> %s（True 和 1 是同一个键，值被覆盖）" % {True: "a", 1: "b"})
print("BB True + True -> %d" % (True + True))
print("BB sum([True, True, False, True]) -> %d（bool 直接当数算）" % sum([True, True, False, True]))
print("BB True.bit_length() -> %d（int 的方法全盘继承）" % True.bit_length())
print("BB ['a', 'b'][True] -> %s（True 当下标 1 用）" % ["a", "b"][True])
