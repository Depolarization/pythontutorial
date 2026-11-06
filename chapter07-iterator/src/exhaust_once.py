"""迭代器一次性语义：耗尽即永久空；zip 复用同一个迭代器的两个经典坑。

测量口径：所有行为直接在真实解释器上实测，try/except 保证退出码 0。
"""
import sys

print("PY " + ".".join(map(str, sys.version_info[:3])))


# == 1. iter / next 手动走一遍 ==
it = iter([10, 20, 30])
print("NEXT 1 -> %r" % next(it))
print("NEXT 2 -> %r" % next(it))
print("NEXT 3 -> %r" % next(it))
try:
    next(it)
except StopIteration:
    print("NEXT 4 -> StopIteration（第一次耗尽）")
try:
    next(it)
except StopIteration:
    print("NEXT 5 -> 还是 StopIteration（永久空，不会自愈）")


# == 2. list 能反复 for，iterator 只能走一遍 ==
lst = [1, 2, 3]
sum1 = sum(lst)
sum2 = sum(lst)
print("LISTTWICE -> %d / %d（每次 for 都重新 iter()，造新迭代器）" % (sum1, sum2))
gen = (x * 10 for x in lst)
g1 = list(gen)
g2 = list(gen)
print("GENTWICE -> %r / %r（同一个迭代器第二次消费：当场空）" % (g1, g2))


# == 3. 坑一：dict(zip(keys, vals)) 复用 vals ==
keys = ["a", "b", "c", "d"]
vals = iter([1, 2, 3])
m1 = dict(zip(keys, vals))
m2 = dict(zip(keys, vals))
print("ZIPDICT 1 -> %r" % (m1,))
print("ZIPDICT 2 -> %r（vals 已被掏空，不报错）" % (m2,))
print("ZIPDROP   -> 键 d 直接丢失（zip 悄悄截到最短，无警告）")


# == 4. 坑二/惯用法：zip(it, it) 成对取 ==
pair = iter([1, 2, 3, 4, 5, 6])
pairs = list(zip(pair, pair))
print("ZIPPAIR  -> %r（同一迭代器喂两个位置：成对消费，不是 15 种组合）" % (pairs,))
triple = iter([1, 2, 3, 4, 5, 6])
triples = list(zip(triple, triple, triple))
print("ZIPTRIPLE -> %r（三元一组同理，尾巴 6 被丢）" % (triples,))


# == 5. 自定义迭代器：__iter__ 返回 self 才是一次性迭代器 ==
class Countdown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self                      # 返回 self：一次性迭代器

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1


c = Countdown(3)
print("CUSTOM 1 -> %r" % (list(c),))
print("CUSTOM 2 -> %r（同一个对象再 for 一次：空）" % (list(c),))
c2 = Countdown(3)
print("CUSTOM 3 -> %r / %r（iter(c2) 返回的还是它自己）" % (list(iter(c2)), list(iter(c2))))
