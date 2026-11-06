import sys
_pa = sys.modules.get("_cyc_a")
if _pa is None:
    print("CYC-FRESH-START -> _cyc_a 还不在 sys.modules，本次 from-import 触发完整加载")
else:
    keys = sorted(k for k in vars(_pa) if not k.startswith("__"))
    print("CYC-PARTIAL -> _cyc_a 在 sys.modules（半成品），业务键=%s" % (keys or "无"))
from _cyc_a import X
Y = "B.Y"
print("[cyc_b] 拿到 X = %r" % X)
