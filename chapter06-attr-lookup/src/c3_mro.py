# -*- coding: utf-8 -*-
"""C3 线性化：两条钻石链的 __mro__ 实测 + 两个最小 TypeError 复现（捕获后退出码 0）。"""
import sys

print("VERSION\t" + sys.version.split()[0])


# == 1. 经典四类钻石
class A:
    def who(self):
        return "A"


class B(A):
    def who(self):
        return "B -> " + super().who()


class C(A):
    def who(self):
        return "C -> " + super().who()


class D(B, C):
    def who(self):
        return "D -> " + super().who()


print("DIAMOND1 MRO -> " + " ".join(k.__name__ for k in D.__mro__))
print("DIAMOND1 CALL -> " + D().who())

# == 2. 混入顺序：写法顺序决定谁赢
class Mixin:
    def who(self):
        return "Mixin"


class Base:
    def who(self):
        return "Base"


class L1(Base, Mixin):        # 写法一：Base 在前
    pass


class L2(Mixin, Base):        # 写法二：Mixin 在前
    pass


print("MIXIN1 MRO -> " + " ".join(k.__name__ for k in L1.__mro__))
print("MIXIN1 CALL -> " + L1().who())
print("MIXIN2 MRO -> " + " ".join(k.__name__ for k in L2.__mro__))
print("MIXIN2 CALL -> " + L2().who())


# == 3. 第二条钻石：菱形顶端是公共基类
class Top:
    def who(self):
        return "Top"


class M1(Top):
    def who(self):
        return "M1 -> " + super().who()


class M2(Top):
    pass


class Leaf2(M1, M2):
    pass


print("DIAMOND2 MRO -> " + " ".join(k.__name__ for k in Leaf2.__mro__))
print("DIAMOND2 CALL -> " + Leaf2().who())

# == 4. 两个单独都合法的类，合在一起就爆（捕获，退出码 0）
try:
    class Bad(L1, L2):        # L1 要 Base 前于 Mixin，L2 要 Mixin 前于 Base
        pass
    print("MRO-ERROR1 -> 居然建出来了")
except TypeError as e:
    print("MRO-ERROR1 -> TypeError: " + str(e))

# == 5. 三类最小复现：子类再次被当作第一个基类
class X:
    pass


class Y(X):
    pass


try:
    class Z(X, Y):            # X 已在 Y 的 MRO 里排 Y 后面，又要排前面 → 矛盾
        pass
    print("MRO-ERROR2 -> 居然建出来了")
except TypeError as e:
    print("MRO-ERROR2 -> TypeError: " + str(e))
