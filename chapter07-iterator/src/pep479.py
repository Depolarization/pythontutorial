"""for 靠 StopIteration 收工：为什么当年会静默截断（机制演示），PEP 479 之后怎么办，
next(it, default) 的适用边界。

本机只有 3.13/3.14（都执行 3.7+ 行为）：3.6 及以前的「静默截断」用手写迭代器
模拟当年生成器帧的行为，画面标注「机制演示，非 3.6 实测」。
"""
import sys

print("PY " + ".".join(map(str, sys.version_info[:3])))


# == 1. for 的编译展开：next + except StopIteration: break ==
def loop_like_for(seq):
    """for x in seq: ... 的等价手写（CPython 字节码 GET_ITER/FOR_ITER 的语义）。"""
    out = []
    it = iter(seq)
    while True:
        try:
            x = next(it)
        except StopIteration:
            break
        out.append(x)
    return out


print("FORLIKE -> %r" % (loop_like_for([1, 2, 3]),))
print("FORLAW  -> for 循环只认一个信号：StopIteration = 我完了")


# == 2. 机制演示（非 3.6 实测）：内部事故为什么会被吞 ==
def inner_api(buf):
    """模拟内部 API：当年不少库用 StopIteration 表示「没数据了」。"""
    if not buf:
        raise StopIteration
    return buf.pop(0)


class OldStyle:
    """模拟 3.6 及以前的生成器帧：体内冒出的 StopIteration 直接出帧。

    3.7+ 的真生成器会拦下来转 RuntimeError；这里用手写迭代器复现那一代行为。
    """

    def __init__(self):
        self.n = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.n >= 2:
            return inner_api([])         # 事故：StopIteration 从这行冒出帧
        self.n += 1
        return self.n * 10


got = []
for v in OldStyle():
    got.append(v)
print("OLDDEMO -> %r（外层 for 分不清「正常耗尽」和「内部事故」，静默收工）" % (got,))


# == 3. 3.7+（PEP 479）实测：生成器内部 raise StopIteration -> RuntimeError ==
def gen():
    yield 1
    yield 2
    raise StopIteration                  # 3.6 及以前：等于正常收工；3.7+：事故上抛


try:
    list(gen())
except RuntimeError as e:
    print("PEP479  -> RuntimeError: %s" % e)


def gen_next(inner):
    yield 1
    yield next(inner)                    # inner 已空：StopIteration 在生成器帧里冒出


it_empty = iter([])
try:
    list(gen_next(it_empty))
except RuntimeError as e:
    print("NEXTIN  -> RuntimeError: %s（生成器里 next 空迭代器同罪）" % e)


# == 4. next(it, default)：default 只对「正常耗尽」有效 ==
def ok_exhaust():
    yield 1


it2 = ok_exhaust()
print("NEXTOK 1 -> %r" % next(it2))
print("NEXTOK 2 -> %r（正常耗尽，default 兜住）" % next(it2, "DEFAULT"))


def bad_gen():
    yield 1
    raise StopIteration


it3 = bad_gen()
print("NEXTBAD 1 -> %r" % next(it3))
try:
    next(it3, "DEFAULT")
except RuntimeError as e:
    print("NEXTBAD 2 -> RuntimeError: %s（default 兜不住内部 raise）" % e)
