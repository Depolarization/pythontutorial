# -*- coding: utf-8 -*-
"""零参数 super() 的协作链：正常一次、点名调用两次、漏调零次、__class__ 隐式 cell 实证。"""
import sys

ORDER = []


# == 1. 协作链：每个 __init__ 只跑一次
class A:
    def __init__(self):
        ORDER.append("A")


class B(A):
    def __init__(self):
        ORDER.append("B")
        super().__init__()


class C(A):
    def __init__(self):
        ORDER.append("C")
        super().__init__()


class D(B, C):
    def __init__(self):
        ORDER.append("D")
        super().__init__()


print("VERSION\t" + sys.version.split()[0])
ORDER.clear()
D()
print("COOP ORDER -> " + " ".join(ORDER))
print("COOP A-TIMES -> " + str(ORDER.count("A")))


# == 2. 打断一：绕过 super 点名直调 → A 跑两次
class A2:
    def __init__(self):
        ORDER.append("A")


class B2(A2):
    def __init__(self):
        ORDER.append("B")
        A2.__init__(self)          # 点名调用，不走 MRO


class C2(A2):
    def __init__(self):
        ORDER.append("C")
        A2.__init__(self)


class D2(B2, C2):
    def __init__(self):
        ORDER.append("D")
        B2.__init__(self)
        C2.__init__(self)


ORDER.clear()
D2()
print("DIRECT ORDER -> " + " ".join(ORDER))
print("DIRECT A-TIMES -> " + str(ORDER.count("A")))


# == 3. 打断二：忘了调 super → B/C/A 跑零次
class D3(B, C):
    def __init__(self):
        ORDER.append("D")          # 只干了自己的活


ORDER.clear()
D3()
print("SKIP ORDER -> " + (" ".join(ORDER) if ORDER else "(空)"))
print("SKIP BCA-TIMES -> " + str(sum(ORDER.count(k) for k in "BCA")))


# == 4. 零参数 super() 依赖编译器塞进闭包的 __class__ cell
class Show:
    def see(self):
        return __class__.__name__ + " 的方法"


print("CLASS-CELL -> " + Show().see())


def borrowed(self):
    super().__init__()


class Host:                        # 把模块级函数挂到类上：没有 __class__ cell
    __init__ = borrowed


try:
    Host()
    print("CELL-BORROW -> 居然成功")
except Exception as e:
    print("CELL-BORROW -> " + type(e).__name__ + ": " + str(e))


class Renamed(A):                  # 换个类名再试：cell 在 def 时就定死了
    def __init__(self):
        super().__init__()


ORDER.clear()
Renamed()
print("CELL-RENAME -> " + " ".join(ORDER) + "（零参数 super 照常工作）")
