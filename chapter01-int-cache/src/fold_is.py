"""257 的身份矩阵：`is` 比的是对象身份，两边各自由哪个常量表提供对象，决定结果。

四个规定场景逐个实测：同一表达式 / 同一 code object 两条语句 /
两个不同函数 / 模块级列表；再对照 REPL 式逐行独立编译。
含字面量的 is 会触发 SyntaxWarning（3.8+），统一用 catch_warnings 收进 stdout。
"""
import sys
import warnings

print("PY " + ".".join(map(str, sys.version_info[:3])))


def ev(expr, env):
    """捕获状态下编译求值；把触发的 SyntaxWarning 原样打印到 stdout。"""
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        r = eval(expr, env)
    for w in ws:
        print("WARN -> %s: %s" % (w.category.__name__, w.message))
    return r


# == A. 同一表达式：两个 257 字面量折进同一张常量表 ==
print("A 同一表达式 257 is 257 -> %s" % ev("257 is 257", {"__builtins__": {}}))


# == B. 同一 code object 的两条独立语句 ==
a = 257
b = 257
print("B 同一函数体 a=257; b=257; a is b -> %s" % (a is b))


# == C. 两个不同函数：各函数常量表里各有一个 257 ==
def f1():
    return 257


def f2():
    return 257


print("C1 同一函数两次调用 f1() is f1() -> %s" % (f1() is f1()))
print("C2 两个不同函数 f1() is f2() -> %s" % (f1() is f2()))


# == D. 模块级列表：字面量仍是模块常量表里的同一个对象 ==
L = [257, 257, 257]
print("D1 模块级列表 L[0] is L[1] -> %s" % (L[0] is L[1]))
print("D2 模块列表 vs 函数 L[0] is f1() -> %s" % (L[0] is f1()))


# == E. REPL 式：赋值与判断拆成两个独立编译的代码对象 ==
g = {}
exec("x = 257", g)
print("E1 REPL 式 x=257 后再问 x is 257 -> %s" % ev("x is 257", g))
g2 = {}
exec("x = 257\ny = 257\nr = x is y", g2)
print("E2 REPL 式 同段 x=257; y=257; x is y -> %s" % g2["r"])


# == F. 经典面试题的原始场景：函数定义也逐行敲，一个 def 一个编译单元 ==
g3 = {}
exec("def f3():\n    return 257", g3)
exec("def f4():\n    return 257", g3)
print("F1 同一文件定义 f1 is f2 -> %s" % (f1() is f2()))
print("F2 逐行定义   f3() is f4() -> %s" % (g3["f3"]() is g3["f4"]()))
