"""3.8+ 对「is 和字面量比较」报 SyntaxWarning：官方口径是这是实现细节，别依赖。

警告在编译期触发，run_py.py 只捕 stdout，所以全部在
warnings.catch_warnings(record=True) 的捕获状态下 compile，再原样打印。
"""
import sys
import warnings

print("PY " + ".".join(map(str, sys.version_info[:3])))


def probe(code_str):
    """编译一段代码，返回触发的警告列表。"""
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        try:
            compile(code_str, "<probe>", "eval")
        except SyntaxError as e:
            return [("SyntaxError", str(e.msg))]
    return [(w.category.__name__, str(w.message)) for w in ws]


# == 1. 哪些写法会警告 ==
CASES = [
    ("x is 257", "is 一个 int 字面量"),
    ("x is 'py'", "is 一个 str 字面量"),
    ("x is (1, 2)", "is 一个元组字面量"),
    ("x == 257", "改用 == 比值"),
    ("x is y", "is 一个名字"),
    ("x is None", "is None（正经哨兵用法）"),
    ("x is True", "is True（单例布尔）"),
]
for code_str, note in CASES:
    got = probe(code_str)
    if got:
        print("W %s -> %s: %s" % (code_str, got[0][0], got[0][1]))
    else:
        print("W %s -> 无警告" % code_str)

# == 2. -W error：警告可以升级成异常 ==
with warnings.catch_warnings(record=True):
    warnings.simplefilter("error", SyntaxWarning)
    try:
        compile("x is 257", "<probe>", "eval")
        print("ERR -W error 模式 -> 没有抛")
    except SyntaxWarning as e:
        print("ERR -W error 模式 -> compile 当场抛 SyntaxWarning: %s" % e)
    except SyntaxError as e:
        print("ERR -W error 模式 -> 升级成 SyntaxError: %s" % e.msg)
