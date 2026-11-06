"""return v 的去向：挂在 StopIteration.value 上；yield from 三层的传递路径；
协程的 return 同源——这就是「协程返回值被吞」的根源。
"""
import sys

print("PY " + ".".join(map(str, sys.version_info[:3])))


# == 1. 生成器里的 return v = raise StopIteration(v) ==
def g():
    yield 1
    yield 2
    return "FINAL"          # 不是函数返回：是「带值的收工信号」


it = g()
print("YIELD 1 -> %r" % next(it))
print("YIELD 2 -> %r" % next(it))
try:
    next(it)
except StopIteration as e:
    print("STOPVAL -> value=%r args=%r" % (e.value, e.args))


# == 2. for 看不见这个返回值（被吞的根源） ==
seen = []
for v in g():
    seen.append(v)
print("FORGET  -> %r（循环体只拿到 yield 的值，FINAL 被 for 扔掉）" % (seen,))


# == 3. 手写驱动才接得住 ==
it2 = g()
vals = []
while True:
    try:
        vals.append(next(it2))
    except StopIteration as e:
        print("DRIVE   -> %r + return %r" % (vals, e.value))
        break


# == 4. yield from：返回值逐层上浮 ==
def inner():
    yield "i1"
    yield "i2"
    return "inner-OK"


def mid():
    got = yield from inner()            # inner 的 return 挂在这
    return "mid[%s]" % got


def outer():
    got = yield from mid()              # mid 的 return 挂在这
    return "outer[%s]" % got


it3 = outer()
path = []
while True:
    try:
        v = next(it3)
        path.append("yield:%r" % v)
    except StopIteration as e:
        path.append("return:%r" % e.value)
        break
print("PATH    -> %s" % "  ->  ".join(path))
print("TREE 1  -> inner:  yield i1, i2; return 'inner-OK'")
print("TREE 2  -> mid:    yield from inner() 收到 'inner-OK'; return 'mid[inner-OK]'")
print("TREE 3  -> outer:  yield from mid() 收到 'mid[inner-OK]'; return 'outer[mid[inner-OK]]'")


# == 5. 协程同源：async def 的 return 也挂在 StopIteration.value ==
async def coro():
    return "协程的返回值"


c = coro()
try:
    c.send(None)              # 手动驱动一步：await 底层就是这么接 return 的
except StopIteration as e:
    print("CORO    -> 驱动完成 StopIteration.value=%r（await 拿到的就是它）" % e.value)
