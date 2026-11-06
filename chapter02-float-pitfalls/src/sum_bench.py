"""同一批金额数据（10 万笔）分别用 float / math.fsum / Decimal(str) / 整数分级（分存 int）
累加，输出误差对比表 + 耗时。金额以整数「分」生成，Decimal(str) 作为精确基准。
纯标准库，只 print。"""
import math
import random
import time
from decimal import Decimal

random.seed(20261105)
N = 100000
cents = [random.randint(1, 10**8) for _ in range(N)]      # 单位：分，0.01 ~ 100 万元
amounts = [c / 100 for c in cents]                        # float 元
exact = Decimal(sum(cents)) / 100                         # 精确总额（元），分母只有 2 和 5


def bench(fn):
    t0 = time.perf_counter()
    v = fn()
    return v, time.perf_counter() - t0


def sum_loop(xs):
    s = 0.0
    for x in xs:
        s += x
    return s


v_float, t_float = bench(lambda: sum_loop(amounts))
v_fsum, t_fsum = bench(lambda: math.fsum(amounts))
v_dec, t_dec = bench(lambda: sum(
    (Decimal("%d.%02d" % divmod(c, 100)) for c in cents), Decimal(0)))
v_int, t_int = bench(lambda: sum(cents))

print("== 10 万笔金额（0.01 ~ 100 万元）四种累加方案 ==")
print("SB N -> %d" % N)
print("SB 精确总额(元) -> %s" % exact)
print("SB 金额范围(元) -> 0.01 ~ 1000000.00")
print("SB 精确值来源 -> 整数「分」求和后除以 100（Decimal 精确）")


def err(v):
    """误差（元）：Decimal(v) 给出该值的精确真值，相减在 28 位精度内完成。"""
    d = (Decimal(v) if isinstance(v, Decimal) else Decimal(v)) - exact
    return d


print("ROW float  顺序累加 -> 结果 %r" % v_float)
print("ROW float  顺序累加误差(元) -> %s" % format(err(v_float).quantize(Decimal("0.000000001")), "f"))
print("ROW float  相对误差 -> %.2e" % abs(float(err(v_float) / exact)))
print("ROW float  耗时 -> %.1f ms" % (t_float * 1000))

print("ROW fsum   math.fsum -> 结果 %r" % v_fsum)
print("ROW fsum   fsum 误差(元) -> %s" % format(err(v_fsum).quantize(Decimal("0.000000001")), "f"))
print("ROW fsum   相对误差 -> %.2e" % abs(float(err(v_fsum) / exact)))
print("ROW fsum   耗时 -> %.1f ms" % (t_fsum * 1000))

print("ROW dec    Decimal(str) -> 结果 %s" % v_dec)
print("ROW dec    误差(元) -> %s" % format(err(v_dec).quantize(Decimal("0.000000001")), "f"))
print("ROW dec    相对误差 -> %s" % Decimal(0))
print("ROW dec    耗时 -> %.1f ms" % (t_dec * 1000))

print("ROW int    分存 int 再除 -> 结果 %s" % (Decimal(v_int) / 100))
print("ROW int    误差(元) -> %s" % Decimal(0))
print("ROW int    相对误差 -> %s" % Decimal(0))
print("ROW int    耗时 -> %.1f ms" % (t_int * 1000))

print("== 结论 ==")
print("CC float 顺序累加 -> 误差不为 0：每一步都对「运行总和」再舍入一次")
print("CC fsum -> 求和本身无舍入（Shewchuk 算法），但输入 float 已是近似值，仍差一点点")
print("CC Decimal(str) -> 从十进制字符串精确构造，运算精确，误差恒为 0")
print("CC 分存 int -> 金额按「分」用整数存，天然精确、最快，展示时再除以 100")
