"""生成器没走完就丢：close()、GeneratorExit、以及收尾拖到 GC 才跑的实测警告。"""
import gc
import sys
import warnings

print("PY " + ".".join(map(str, sys.version_info[:3])))


# == 1. close()：把 GeneratorExit 投进暂停点 ==
def g_clean():
    try:
        yield 1
        yield 2
    except GeneratorExit:
        print("GENEXIT -> 在 yield 暂停点收到 GeneratorExit")
        raise                       # 清理完继续抛，生成器才算正常关闭


it = g_clean()
print("NEXT    -> %r（生成器暂停在第一个 yield）" % next(it))
it.close()
print("CLOSED  -> close() 返回，生成器已关闭")


# == 2. 吞掉 GeneratorExit 还想再 yield -> RuntimeError ==
def g_greedy():
    try:
        yield 1
    except GeneratorExit:
        yield "还想再吐一个"          # 禁止：关闭途中不许再产出


it2 = g_greedy()
print("NEXT2   -> %r" % next(it2))
try:
    it2.close()
except RuntimeError as e:
    print("IGNORE  -> RuntimeError: %s" % e)


# == 3. 不调 close：丢引用 + GC 收尾（实测 RuntimeWarning） ==
CLEANED = []


def g_lazy():
    try:
        yield 1
        yield 2
    finally:
        CLEANED.append("finally 跑了")
        warnings.warn("生成器没耗尽就被丢弃：收尾拖到最后一个引用消失才跑", RuntimeWarning)


with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter("always")
    it3 = g_lazy()
    next(it3)                       # 只走一步，没走完
    print("ALIVE   -> 生成器还挂着引用：CLEANED=%r" % (CLEANED,))
    del it3                         # 最后一个引用消失
    gc.collect()
    print("DROPPED -> 引用已丢 + gc.collect()：CLEANED=%r" % (CLEANED,))
    for w in ws:
        print("WARN    -> %s: %s" % (w.category.__name__, w.message))
