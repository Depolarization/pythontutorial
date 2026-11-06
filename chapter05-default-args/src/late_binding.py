# 选题5 探针B：闭包捕获变量而非值 —— 循环里的 lambda 全返回同一个数，三种修复逐个实测
# 纯标准库；只 print 不写文件；约定「KEY -> 值」行供网页取数
import functools, sys

print("EXPL", "->", sys.version.split()[0])

# == A. 最小复现：三种写法全中招 ==
lams = [lambda: i for i in range(3)]
print("LB listcomp", "->", [f() for f in lams])

lams2 = []
for j in range(3):
    lams2.append(lambda: j)
print("LB forloop", "->", [f() for f in lams2])

handlers = []
for k in range(3):
    handlers.append(lambda: k * 10)
print("LB handlers", "->", [h() for h in handlers])

# == B. 证据：cell_contents 全是同一个最终值 ==
print("CELL 0", "->", lams[0].__closure__[0].cell_contents)
print("CELL 1", "->", lams[1].__closure__[0].cell_contents)
print("CELL 2", "->", lams[2].__closure__[0].cell_contents)
print("CELL same", "->", lams[0].__closure__[0] is lams[2].__closure__[0])
print("CELL 循环变量 j", "->", j)

# == C. 修复一：默认参数 i=i，在 def 时固化 ==
fix1 = [lambda i=i: i for i in range(3)]
print("FIX1 调用", "->", [f() for f in fix1])
print("FIX1 defaults", "->", [f.__defaults__[0] for f in fix1])

# == D. 修复二：functools.partial 把值绑进位置参数 ==
fix2 = [functools.partial(lambda k: k, i) for i in range(3)]
print("FIX2 调用", "->", [f() for f in fix2])
print("FIX2 args", "->", [p.args for p in fix2])

# == E. 修复三：工厂函数包一层，每轮调用有自己的作用域 ==
def make(k):
    return lambda: k

fix3 = [make(i) for i in range(3)]
print("FIX3 调用", "->", [f() for f in fix3])
print("FIX3 cells", "->", [f.__closure__[0].cell_contents for f in fix3])
