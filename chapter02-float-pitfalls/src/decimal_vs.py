"""Decimal(str) vs Decimal(float) 的天壤之别；Fraction 精确有理数。
Fraction 只保证「运算」精确，输入是 float 时输入本身已带误差。纯标准库，只 print。"""
from decimal import Decimal, getcontext
from fractions import Fraction

print("== Decimal(str) vs Decimal(float) ==")
print("DV Decimal('0.1') -> %s" % Decimal("0.1"))
print("DV Decimal(0.1)   -> %s" % Decimal(0.1))
print("DV 两者相等 -> %s（一个是你以为的 0.1，一个是 float 0.1 的精确真值）" %
      (Decimal("0.1") == Decimal(0.1)))
print("DV Decimal('0.1')+Decimal('0.2') -> %s" % (Decimal("0.1") + Decimal("0.2")))
print("DV 和等于 Decimal('0.3') -> %s" % (Decimal("0.1") + Decimal("0.2") == Decimal("0.3")))
print("DV Decimal(0.1)+Decimal(0.2) -> %s" % (Decimal(0.1) + Decimal(0.2)))
print("DV 和等于 Decimal(0.3) -> %s（喂进去的是二进制近似值，Decimal 也救不回来）" %
      (Decimal(0.1) + Decimal(0.2) == Decimal(0.3)))

print("== Decimal 的除法在上下文精度内会舍入 ==")
print("DV 上下文精度 -> %d 位" % getcontext().prec)
print("DV Decimal(1)/Decimal(3) -> %s" % (Decimal(1) / Decimal(3)))
print("DV (1/3)*3 -> %s（差万分之一，不是 1）" % (Decimal(1) / Decimal(3) * 3))

print("== Fraction：精确有理数，分子分母都是任意精度整数 ==")
print("FR Fraction('0.1') -> %s" % Fraction("0.1"))
print("FR Fraction(0.1) -> %s（float 输入的精确二进制展开）" % Fraction(0.1))
print("FR Fraction(1,3)*3 == 1 -> %s" % (Fraction(1, 3) * 3 == 1))
print("FR Fraction('0.1')+Fraction('0.2') == Fraction('0.3') -> %s" %
      (Fraction("0.1") + Fraction("0.2") == Fraction("0.3")))
print("FR Fraction(0.1)+Fraction(0.2) == Fraction(0.3) -> %s（输入是 float，一样救不回）" %
      (Fraction(0.1) + Fraction(0.2) == Fraction(0.3)))
print("FR Fraction(1,10)+Fraction(2,10) -> %s（自动约分）" % (Fraction(1, 10) + Fraction(2, 10)))
print("FR float(Fraction(1,3)) -> %s（输出时才转 float）" % float(Fraction(1, 3)))

print("== 一句话选型 ==")
print("PICK 记账/金额 -> Decimal(str) 或整数分；需要分数运算（配比/利率） -> Fraction")
print("PICK 统计/科学计算 -> 直接 float，比较用 math.isclose")
