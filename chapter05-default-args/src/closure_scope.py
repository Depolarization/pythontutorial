# 选题5 探针C：列表推导自带作用域、循环变量不泄漏；普通 for 的循环变量泄漏到外层
# 纯标准库；只 print 不写文件；约定「KEY -> 值」行供网页取数
import sys, types

print("EXPL", "->", sys.version.split()[0])

# == A. 普通 for 的循环变量泄漏到外层 ==
leak = 0
for leak in range(3):
    pass
print("LEAK for 循环后", "->", leak)

# == B. 推导式的变量不进外层作用域 ==
try:
    [comp for comp in range(3)]
    ref = comp                 # 真正去引用推导式的循环变量
    print("COMP 引用 comp", "->", "没有报错，拿到 " + repr(ref))
except NameError as e:
    print("COMP 引用 comp", "->", type(e).__name__ + ": " + str(e))

# == C. 推导式不覆盖外层同名变量，for 会覆盖 ==
outer = "外面"
[outer for outer in range(3)]
print("SHADOW listcomp", "->", outer)

outer2 = "外面"
gen = (outer2 for outer2 in range(3))
print("SHADOW genexp", "->", outer2)
print("SHADOW genexp vals", "->", list(gen))

outer3 = "外面"
for outer3 in range(3):
    pass
print("SHADOW for", "->", outer3)

# == D. 作用域是自己的，晚绑定照旧 ==
lams = [lambda: k for k in range(3)]
print("SCOPE latebind", "->", [f() for f in lams])

# == E. 实现机制实测：推导式变量藏在独立的隐藏槽位里（3.12+ 内联进外层帧） ==
co = compile("[x for x in range(3)]", "<probe>", "eval")
print("SCOPE 隐藏局部", "->", co.co_varnames)
print("SCOPE 独立嵌套函数", "->", [c.co_name for c in co.co_consts
                                   if isinstance(c, types.CodeType)])
co2 = compile("[lambda: i for i in range(3)]", "<probe>", "eval")
print("SCOPE 闭包时变 cell", "->", co2.co_cellvars)
