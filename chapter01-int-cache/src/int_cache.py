"""小整数缓存：CPython 预先把 -5..256 这 262 个 int 做成全局单例。

测量手法：eval 每次编译一个独立代码对象，两次求值的结果要同身份，
常量折叠帮不上忙（各编各的常量表）——只能来自全局对象缓存。
"""
import sys

print("PY " + ".".join(map(str, sys.version_info[:3])))


# == 1. 两次独立编译比身份 ==
def twice(expr):
    """同一表达式字符串独立编译求值两次，比对象身份。"""
    return eval(expr) is eval(expr)


for v in (-6, -5, 0, 1, 100, 200, 256, 257, 258, 1000):
    print("TWICE %-5d -> %s" % (v, twice(str(v))))

lo = hi = None
for v in range(-10, 300):
    if twice(str(v)):
        if lo is None:
            lo = v
        hi = v
print("RANGE 扫描 -10..299 -> %d..%d" % (lo, hi))


# == 2. 跨函数对拍：缓存内的 200 与缓存外的 257 ==
def f_200a():
    return 200


def f_200b():
    return 200


def f_257a():
    return 257


def f_257b():
    return 257


print("CROSS 200 两个函数 -> %s" % (f_200a() is f_200b()))
print("CROSS 257 两个函数 -> %s" % (f_257a() is f_257b()))


# == 3. 引用计数看缓存 ==
x = 257
print("REF 256          -> %d" % sys.getrefcount(256))
print("REF 257          -> %d" % sys.getrefcount(257))
big = 2 ** 40
print("REF big(2**40)   -> %d" % sys.getrefcount(big))
refs = [big] * 8
print("REF big 8个引用后 -> %d（+8）" % sys.getrefcount(big))
