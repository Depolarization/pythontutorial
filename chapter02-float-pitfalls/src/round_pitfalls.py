"""round 的两个坑分清：坑 A round(2.675, 2)==2.67 是十进制字面量早就错了（存储值略小）；
坑 B round(0.5)==0 才是银行家舍入（round-half-even）。纯标准库，只 print。"""
from decimal import Decimal, ROUND_HALF_UP

print("== 坑 A：round(2.675, 2) 得 2.67 —— 错在字面量，不在 round ==")
print("A hex(2.675) -> %s" % (2.675).hex())
print("A Decimal(2.675) 精确存储值 -> %s" % Decimal(2.675))
print("A round(2.675, 2) -> %s" % round(2.675, 2))
print("A format(2.675, '.2f') -> %s" % format(2.675, ".2f"))
print("A 存储值 2.674999… 严格小于 2.675：无平局，怎么舍都是 2.67")
print("A Decimal('2.675').quantize(0.01) 默认 half-even -> %s" %
      Decimal("2.675").quantize(Decimal("0.01")))
print("A Decimal('2.675').quantize(0.01) HALF_UP 四舍五入 -> %s" %
      Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
print("A 对照 1.005：round(1.005, 2) -> %s" % round(1.005, 2))
print("A 对照 1.005 的存储值 -> %s" % Decimal(1.005))

print("== 坑 B：round(0.5) == 0 —— 这才是银行家舍入（round-half-even）==")
for v in ("0.5", "1.5", "2.5", "3.5", "4.5", "-0.5", "-1.5", "-2.5"):
    print("B round(%s) -> %d" % (v, round(float(v))))
print("B 规律 -> 偶数邻居胜出：0.5→0、1.5→2、2.5→2、3.5→4、4.5→4")
print("B x.5 都能被二进制精确表示：真平局，才轮到 half-even 出场")
print("B HALF_UP 期望 round(0.5) 是 1，实测 0；round(2.5) 期望 3，实测 2")
print("B Decimal 默认也是 half-even：Decimal('2.5') 取整 -> %s" %
      Decimal("2.5").quantize(Decimal("1")))
print("B Decimal('3.5') 取整 -> %s" % Decimal("3.5").quantize(Decimal("1")))

print("== 两个坑一句话分开 ==")
print("SUMMARY 坑A -> 字面量准头问题：2.675 存进来就变成 2.674999…，与舍入规则无关")
print("SUMMARY 坑B -> 规则问题：round 用 round-half-even（银行家），平局不总是进位")
