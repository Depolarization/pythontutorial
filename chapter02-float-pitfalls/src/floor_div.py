"""// 向负无穷取整：-7 // 2 == -4、-7 % 2 == 1（余数符号跟除数，和 C/Java 截断相反）。
divmod 恒等式 (a//b)*b + a%b == a 在 10 万随机正负数上全量验证。纯标准库，只 print。"""
import math
import random
import time

print("== -7 // 2 == -4：floor（向负无穷）语义 ==")
print("FD -7 // 2 -> %d" % (-7 // 2))
print("MD -7 %% 2 -> %d" % (-7 % 2))
print("FD 7 // 2 -> %d" % (7 // 2))
print("MD 7 %% 2 -> %d" % (7 % 2))
print("FD 7 // -2 -> %d" % (7 // -2))
print("MD 7 %% -2 -> %d" % (7 % -2))
print("FD -7 // -2 -> %d" % (-7 // -2))
print("MD -7 %% -2 -> %d" % (-7 % -2))
print("DM divmod(-7, 2) -> %s" % (divmod(-7, 2),))
print("DM divmod(7, -2) -> %s" % (divmod(7, -2),))
print("MD 规律 -> 余数符号永远跟除数 b；商 = floor(a/b) 向负无穷取整")

print("== 与 C/Java 相反：那边是截断（trunc），余数符号跟被除数 ==")
def c_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q
def c_mod(a, b):
    return a - c_div(a, b) * b
print("C trunc(-7/2) -> %d" % math.trunc(-7 / 2))
print("C C/Java 的 -7/2 -> %d（Python 给 -4）" % c_div(-7, 2))
print("C C/Java 的 -7%%2 -> %d（符号跟被除数；Python 给 1）" % c_mod(-7, 2))
print("C C/Java 的 7%%-2 -> %d（Python 给 -1，同为负但归属相反）" % c_mod(7, -2))
print("C Python 的 int() 才是截断：int(-3.7) -> %d；-3.7 // 1 -> %s" % (int(-3.7), -3.7 // 1))

print("== float 也是同一套 floor 语义 ==")
print("FL -7.0 // 2 -> %s" % (-7.0 // 2))
print("FL -7.5 %% 2 -> %s" % (-7.5 % 2))
print("FL -0.1 %% 1 -> %s" % (-0.1 % 1))
print("FL 5.5 %% -2 -> %s" % (5.5 % -2))

print("== divmod 恒等式：(a//b)*b + a%b == a，10 万随机正负数 ==")
random.seed(20261105)
N = 100000
t0 = time.perf_counter()
bad_i = 0
for _ in range(N):
    a = random.randint(-10**18, 10**18)
    b = random.choice([-1, 1]) * random.randint(1, 10**9)
    if (a // b) * b + a % b != a:
        bad_i += 1
t_i = time.perf_counter() - t0
print("ID int    组数 -> %d" % N)
print("ID int    不成立数 -> %d" % bad_i)
print("ID int    全量成立 -> %s" % (bad_i == 0))
print("ID int    耗时 -> %.3f s" % t_i)

t0 = time.perf_counter()
bad_f = 0
tested_f = 0
for _ in range(N):
    a = random.uniform(-1e6, 1e6)
    b = random.uniform(-100, 100)
    if abs(b) < 1e-9:
        continue
    tested_f += 1
    if (a // b) * b + a % b != a:
        bad_f += 1
t_f = time.perf_counter() - t0
print("ID float  组数 -> %d" % tested_f)
print("ID float  不成立数 -> %d（int 恒等式有保证；float 是近似，极端比值下差 1 个 ulp）" % bad_f)
print("ID float  耗时 -> %.3f s" % t_f)
