"""dis 与 co_consts 证据：同一 code object 里写几次 257，常量表里只有一个对象；
LOAD_CONST 复用同一个；两个函数各带各的常量表。
"""
import dis
import io
import sys

print("PY " + ".".join(map(str, sys.version_info[:3])))

# == 1. 同一 code object：co_consts 只存一个 257 ==
SRC = "a = 257\nb = 257\n"
code = compile(SRC, "<fold>", "exec")
n_in_src = SRC.count("257")
consts = [c for c in code.co_consts if isinstance(c, int) and c == 257]
uniq = len({id(c) for c in consts})
print("SRC 源码里 257 写了 %d 次 -> co_consts 里 %d 个 257 对象" % (n_in_src, uniq))
print("CONSTS co_consts -> %r" % (code.co_consts,))

buf = io.StringIO()
dis.dis(code, file=buf)
for ln in buf.getvalue().splitlines():
    print("DIS| " + ln)

# == 2. 两个函数各带各的常量表 ==
def fa():
    return 257


def fb():
    return 257


ca, cb = fa.__code__, fb.__code__
print("FUNCS fa.co_consts -> %r" % (ca.co_consts,))
print("FUNCS fb.co_consts -> %r" % (cb.co_consts,))
print("FUNCS 两表的 257 同一对象 -> %s" % (ca.co_consts[0] is cb.co_consts[0]))
print("FUNCS fa() is fb() -> %s" % (fa() is fb()))

# == 3. 独立编译 = 独立对象；引用计数如实累加 ==
c1 = compile("257", "<t1>", "eval")
c2 = compile("257", "<t2>", "eval")
print("TWOCODE 两个独立编译的 257 -> %s" % (c1.co_consts[0] is c2.co_consts[0]))
obj = ca.co_consts[0]
print("REF 函数常量里的 257 -> %d" % sys.getrefcount(obj))
also = obj
print("REF 再持一个引用后 -> %d" % sys.getrefcount(obj))
