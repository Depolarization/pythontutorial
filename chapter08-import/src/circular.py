"""循环导入现场：真实报错两种措辞（顶级模块 / 包内模块）、半成品状态、
入口反转、报错提示由 __spec__ 现场决定；三种解法逐个跑。"""
import sys

# == 1. 顶级模块对：a 顶部 import _cyc_b，b 顶部 from _cyc_a import X —— 当场爆
try:
    import _cyc_a
except Exception as e:
    print("CYC-ERROR -> %s: %s" % (type(e).__name__, e))
print("CYC-A-IN-MODULES -> %s" % ("_cyc_a" in sys.modules))
print("CYC-B-IN-MODULES -> %s" % ("_cyc_b" in sys.modules))

# == 2. 包内模块对：同构的循环，报错换上经典措辞
try:
    import _cycpkg.a
except Exception as e:
    print("CYC-PKG-ERROR -> %s: %s" % (type(e).__name__, e))

# == 3. 入口换成 _cyc_b：同一对顶级模块，这次跑通了
import _cyc_b
A_full = sys.modules["_cyc_a"]      # import 失败的名字不会绑进本模块，从 sys.modules 拿
print("ENTRY-B-Y -> %s" % _cyc_b.Y)
print("ENTRY-B-SEES-X -> %s" % A_full.X)
print("ENTRY-B-A-FULL -> %s" % hasattr(A_full, "X"))
print("ENTRY-B-IN-MODULES -> %s" % ("_cyc_a" in sys.modules and "_cyc_b" in sys.modules))

# == 4. 解法一：延迟 import —— 把 from 挪进函数体，调用那一刻 a 早已初始化完
import _cycd1_a
import _cycd1_b
print("FIX1-RESULT -> %s" % _cycd1_b.late_x())

# == 5. 解法二：import x 用 x.y —— 顶部只绑模块对象，属性运行期再取
import _cycd2_a
import _cycd2_b
print("FIX2-RESULT -> %s" % _cycd2_b.read_x())

# == 6. 解法三：拆模块 —— 公共内容下沉到第三个模块，环从结构上消失
import _cycd3_a
import _cycd3_b
print("FIX3-A -> %s" % _cycd3_a.show())
print("FIX3-B -> %s" % _cycd3_b.show())
