"""浅拷贝保留内部对象 identity：两份独立浅拷贝的内层仍是同一个对象；
浅拷贝只复制一层，更深的嵌套照样共享；deepcopy 在一棵树内保留别名。
改内层会穿透浅拷贝——这是共享 identity 的直接后果。"""
import copy
import sys

# == 1. 两份浅拷贝，三方共享同一个内层对象 ==
a = [[1, 2], [3, 4]]
b1 = list(a)
b2 = copy.copy(a)
print("VERSION\t%s" % sys.version.split()[0])
print("COPY1\tb1=list(a) b2=copy.copy(a)：新外壳=%s" % (b1 is not a and b2 is not a))
print("ID1\ta[0]=%s b1[0]=%s b2[0]=%s 三方同一对象=%s" %
      (hex(id(a[0])), hex(id(b1[0])), hex(id(b2[0])), b1[0] is b2[0] is a[0]))

# == 2. 浅拷贝只复制一层，更深的嵌套照旧共享 ==
a2 = [[[5]]]
s2 = a2[:]
nested_ok = (s2[0] is a2[0]) and (s2[0][0] is a2[0][0])
print("NESTED\ta2=[[ [5] ]] 浅拷贝后：s2[0] is a2[0]=%s  s2[0][0] is a2[0][0]=%s" %
      (s2[0] is a2[0], s2[0][0] is a2[0][0]))
s2[0][0][0] = 99
print("EFFECT\t通过浅拷贝改最内层 → 原始 a2[0][0][0] 跟着=%d（共享 identity 的直接后果）" %
      a2[0][0][0])

# == 3. deepcopy 保别名：一棵树内的共享引用，拷完还是共享 ==
x = [1, 2]
tree = [x, x]
dd = copy.deepcopy(tree)
alias_ok = dd[0] is dd[1]
print("ALIAS\tx 被引用两次 → deepcopy 后 d[0] is d[1]=%s（别名保留，不复制成两份）" % alias_ok)
print("SELF-OK\t%d/3" % ((b1[0] is b2[0] is a[0]) + nested_ok + alias_ok))
