"""任意精度整数：没有溢出，只有内存账。

CPython 的 int 按 30 位一节（digit）的无符号数组存储（64 位平台），
__sizeof__ 随二进制位数按「每 30 位 +一个 digit」的台阶增长，
与 sys.int_info.bits_per_digit 对拍。
"""
import sys

print("PY " + ".".join(map(str, sys.version_info[:3])))

ii = sys.int_info
print("INTINFO bits_per_digit=%d sizeof_digit=%d" % (ii.bits_per_digit, ii.sizeof_digit))

# == 1. 2**1000 不溢出；float 同一口径直接溢出 ==
p = 2 ** 1000
print("POWDEC 2**1000 十进制位数 -> %d" % len(str(p)))
print("POWBIT 2**1000 二进制位数 -> %d" % p.bit_length())
print("POWSIZE 2**1000 __sizeof__ -> %d" % p.__sizeof__())
try:
    float(2 ** 1000)
    print("FLOAT float(2**1000) -> 成功（在 float 上限内）")
except OverflowError:
    print("FLOAT float(2**1000) -> OverflowError")
try:
    float(2 ** 1024)
    print("FLOAT float(2**1024) -> 成功")
except OverflowError:
    print("FLOAT float(2**1024) -> OverflowError")

# == 2. __sizeof__ 台阶 ==
for n in (0, 1, 29, 30, 59, 60, 89, 90, 119, 120, 999, 1000):
    v = 2 ** n
    print("SIZE 2**%-4d -> bit_length=%-5d __sizeof__=%d" % (n, v.bit_length(), v.__sizeof__()))

steps = [n for n in range(1, 121)
         if (2 ** n).__sizeof__() != (2 ** (n - 1)).__sizeof__()]
print("STEPS 1..120 里 sizeof 增长的 n -> %s" % steps)

hdr = (2 ** 0).__sizeof__() - ii.sizeof_digit
ok = all((2 ** n).__sizeof__() == hdr + ii.sizeof_digit * ((n + 30) // 30)
         for n in range(0, 301))
print("FORMULA __sizeof__ == %d + %d*ceil((n+1)/%d) 对拍 n=0..300 -> %s"
      % (hdr, ii.sizeof_digit, ii.bits_per_digit, ok))

# == 3. 大整数的另一道护栏：int -> str 的位数上限（3.11+） ==
print("STRLIMIT len(str(2**1000)) -> %d（< 4300 可以转）" % len(str(2 ** 1000)))
try:
    len(str(2 ** 20000))
    print("STRLIMIT len(str(2**20000)) -> 成功")
except ValueError as e:
    print("STRLIMIT len(str(2**20000)) -> ValueError: %s" % e)
