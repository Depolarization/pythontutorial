import _pkgcounter
_pkgcounter.N += 1
print("[_pkgdemo] __init__ 执行（第 %d 次）" % _pkgcounter.N)
from . import mod_b          # side-effect import：__init__ 顺手把子模块拉进来
VERSION = "1.0"
