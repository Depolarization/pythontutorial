"""0.1 + 0.2 != 0.3：用 float.hex() 看真实存储值，讲清二进制浮点为什么存不下 0.1。
另附 math.isclose 的正确用法。纯标准库，只 print 不写文件。"""
import math
import struct
from decimal import Decimal
from fractions import Fraction

print("== 0.1 + 0.2 与 0.3 的真实存储 ==")
print("HEX 0.1 -> %s" % (0.1).hex())
print("HEX 0.2 -> %s" % (0.2).hex())
print("HEX 0.3 -> %s" % (0.3).hex())
print("HEX sum -> %s" % (0.1 + 0.2).hex())
print("EQ 0.1+0.2 == 0.3 -> %s" % (0.1 + 0.2 == 0.3))
print("SUB (0.1+0.2) - 0.3 -> %r" % ((0.1 + 0.2) - 0.3))
print("ULP ulp(0.3) -> %r" % math.ulp(0.3))
bits01 = int(struct.pack(">d", 0.1).hex(), 16)
print("BYTES 0.1 内存字节(大端) -> %s" % struct.pack(">d", 0.1).hex())
print("BITS 0.1 符号 -> %d  指数域 -> %d（真指数 %d）  尾数域 -> 0x%x" %
      (bits01 >> 63, (bits01 >> 52) & 0x7FF, ((bits01 >> 52) & 0x7FF) - 1023, bits01 & ((1 << 52) - 1)))

print("== 每个 double 的精确十进制真值（Decimal(float) 不做任何舍入）==")
print("EXACT 0.1 -> %s" % Decimal(0.1))
print("EXACT 0.2 -> %s" % Decimal(0.2))
print("EXACT 0.3 -> %s" % Decimal(0.3))
print("EXACT sum -> %s" % Decimal(0.1 + 0.2))
print("EXACT sum 比 0.3 的存储值大 -> %s" % (Decimal(0.1 + 0.2) - Decimal(0.3)))

print("== 为什么存不下 0.1：0.1 的二进制是无限循环小数 ==")
x = Fraction(1, 10)
bits = ""
for _ in range(28):
    x *= 2
    if x >= 1:
        bits += "1"
        x -= 1
    else:
        bits += "0"
print("BIN 0.1 的二进制前 28 位 -> 0.%s…" % bits)
f = Fraction(0.1)
print("FRAC float(0.1) 的精确分数 -> %d/%d" % (f.numerator, f.denominator))
print("FRAC 分母 -> 2 的 55 次方（double 一律是 k/2^e，没有 1/10 这种分数）")
d = Fraction(0.1) - Fraction(1, 10)
print("FRAC float(0.1) 与真值 1/10 的差 -> %s ≈ %s" % (d, float(d)))

print("== 正确比较：math.isclose ==")
print("IC (0.1+0.2)==0.3 -> %s" % ((0.1 + 0.2) == 0.3))
print("IC isclose(0.1+0.2, 0.3) -> %s" % math.isclose(0.1 + 0.2, 0.3))
print("IC 默认 rel_tol -> 1e-09（容差随量级放大）")
print("IC isclose(1e10, 1e10+1) -> %s（差 1，但容差是 10）" % math.isclose(1e10, 1e10 + 1))
print("IC isclose(1e-9, 0.0) -> %s（rel_tol 对 0 失效）" % math.isclose(1e-9, 0.0))
print("IC isclose(1e-9, 0.0, abs_tol=1e-8) -> %s（比 0 必须给 abs_tol）" %
      math.isclose(1e-9, 0.0, abs_tol=1e-8))
