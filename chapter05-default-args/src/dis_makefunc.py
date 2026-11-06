# 选题5 探针E：dis 证据 —— def 行现场构造默认值对象并挂进 MAKE_FUNCTION；
#              晚绑定 lambda 读 cell（LOAD_DEREF），修复后读自己的默认参数（LOAD_FAST）
# 纯标准库；只 print 不写文件；约定「KEY -> 值」与「TAG|反汇编行」
# 注意：dis 输出里的 <code object ... at 0x...> 地址随运行变化、与解释器版本无关，
#       统一抹平成 0x…，让两列逐行对比只反映指令结构差异。
import dis, io, re, sys, types

print("EXPL", "->", sys.version.split()[0])

_ADDR = re.compile(r"0x[0-9a-fA-F]+")

def dump(tag, co):
    buf = io.StringIO()
    dis.dis(co, depth=0, file=buf)
    for line in buf.getvalue().splitlines():
        print(tag + "|" + _ADDR.sub("0x…", line))

# == A. def f(x=[]) 的字节码：默认值对象在 def 行现场构造，MAKE_FUNCTION 挂上 defaults ==
SRC = "def f(x=[]):\n    x.append(1)\n    return x"
code = compile(SRC, "<probe>", "exec")
dump("DISA", code)

mod = {"__name__": "probe"}
exec(code, mod)
f = mod["f"]
print("MAKEFUNC defaults", "->", f.__defaults__)
print("MAKEFUNC 类型", "->", type(f.__defaults__).__name__)
d0 = f.__defaults__[0]
f()
f()
f()
print("MAKEFUNC same list", "->", f.__defaults__[0] is d0)
print("MAKEFUNC 3 次调用后", "->", f.__defaults__[0])

# == B. 晚绑定：推导式内联在外层帧，i 是 cell；MAKE_FUNCTION 挂 closure，lambda 体 LOAD_DEREF ==
code_lb = compile("lams = [lambda: i for i in range(3)]", "<probe>", "exec")
lam = next(c for c in code_lb.co_consts if isinstance(c, types.CodeType))
print("CELLVARS 外层帧", "->", code_lb.co_cellvars)
dump("DISB", code_lb)
dump("DISC", lam)
lb_ops = sorted({ins.opname for ins in dis.get_instructions(lam)})
print("DEREF 未修复 lambda 的读法", "->", " ".join(lb_ops))

# == C. 修复后：lambda i=i 里默认值在 def 时打包进 defaults，lambda 体 LOAD_FAST ==
code_fx = compile("fix = [lambda i=i: i for i in range(3)]", "<probe>", "exec")
lam2 = next(c for c in code_fx.co_consts if isinstance(c, types.CodeType))
print("CELLVARS 修复后外层帧", "->", code_fx.co_cellvars)
dump("DISD", code_fx)
dump("DISE", lam2)
fx_ops = sorted({ins.opname for ins in dis.get_instructions(lam2)})
print("FAST 修复后 lambda 的读法", "->", " ".join(fx_ops))
