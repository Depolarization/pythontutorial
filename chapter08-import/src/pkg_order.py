"""包的 __init__.py 执行顺序：父包先行、子模块导入不重跑 __init__、side-effect import。"""
import sys
import _pkgcounter

# == 1. 只 import 包本体：__init__ 执行，side-effect 把 mod_b 一起拉进来
import _pkgdemo
print("PKG-INIT-EXEC -> %d" % _pkgcounter.N)
print("SIDE-EFFECT-MOD-B -> %s" % ("_pkgdemo.mod_b" in sys.modules))
print("PKG-VERSION -> %s" % _pkgdemo.VERSION)
print("PKG-FILE -> %s" % _pkgdemo.__file__)

# == 2. 再 import 子模块 mod_a：__init__ 不会重跑
import _pkgdemo.mod_a
print("INIT-AFTER-SUB -> %d" % _pkgcounter.N)
print("SUB-NAME -> %s" % _pkgdemo.mod_a.NAME)
print("PKG-ATTR-AUTO -> %s" % (_pkgdemo.mod_a is sys.modules["_pkgdemo.mod_a"]))
print("REL-IMPORT -> %s" % _pkgdemo.mod_a.b_name())

# == 3. 直接 import 子包的子模块：父包 __init__ 仍然先执行
import _pkgdemo2.mod_a
print("PKG2-INIT-EXEC -> %d" % _pkgcounter.N)
print("PKG2-SUB-NAME -> %s" % _pkgdemo2.mod_a.NAME)
from _pkgdemo import mod_b as mb
print("FROM-PKG-MOD -> %s" % mb.NAME)
