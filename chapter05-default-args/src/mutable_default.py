# 选题5 探针A：可变默认参数 —— 默认值在 def 执行时求值一次，跨调用共享同一个对象
# 纯标准库；只 print 不写文件；约定「KEY -> 值」行供网页取数
import sys

print("EXPL", "->", sys.version.split()[0])

# == A. 最小复现：默认列表跨调用累积 ==
def acc(item, basket=[]):
    basket.append(item)
    return basket

print("ACC 1", "->", acc("a"))
print("ACC 2", "->", acc("b"))
print("ACC 3", "->", acc("c"))
print("ACC len", "->", len(acc.__defaults__[0]))
print("ACC defaults", "->", acc.__defaults__)

# == B. __defaults__ is 证据：def 时挂上的就是那个对象 ==
TARGET = ["出厂"]

def with_target(x=TARGET):
    x.append(len(x))
    return x

print("SAME 1 defaults0 is TARGET", "->", with_target.__defaults__[0] is TARGET)
print("SAME 2 返回值 is TARGET", "->", with_target() is TARGET)
with_target()
with_target()
print("SAME 3 TARGET 被改写", "->", TARGET)
print("SAME 4 __defaults__ 元组", "->", with_target.__defaults__)

# == C. 求值时机：默认表达式在 def 行执行时只算一次 ==
EVALS = 0

def _fresh():
    global EVALS
    EVALS += 1
    return []

def evaluated_once(x=_fresh()):
    return x

print("TIMES def 时求值次数", "->", EVALS)
evaluated_once()
evaluated_once()
evaluated_once()
print("TIMES 3 次调用后求值次数", "->", EVALS)
print("TIMES 两次缺省调用同一对象", "->", evaluated_once() is evaluated_once())

# == D. None 哨兵：每次调用现场新建 ==
def safe(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item)
    return basket

s1 = safe("x")
s2 = safe("y")
print("SENT 1 第一次", "->", s1)
print("SENT 2 第二次", "->", s2)
print("SENT 3 两次结果 is", "->", s1 is s2)
print("SENT 4 safe __defaults__", "->", safe.__defaults__)

# == E. 不可变默认值：绑定改不动，跨调用无残留 ==
def s_with(x="p"):
    x = x + "!"
    return x

def t_with(x=()):
    x = x + ("#",)
    return x

def i_with(x=0):
    x = x + 1
    return x

print("IMMUT str", "->", "%s %s %s" % (s_with(), s_with(), s_with()))
print("IMMUT tuple", "->", "%s %s" % (t_with(), t_with()))
print("IMMUT int", "->", "%s %s" % (i_with(), i_with()))
print("IMMUT 原默认未被改", "->", "%s %s %s" % (s_with.__defaults__, t_with.__defaults__, i_with.__defaults__))
