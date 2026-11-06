import sys
_pa = sys.modules.get("_cycpkg.a")
if _pa is None:
    print("CYC-PKG-PARTIAL -> 不在 sys.modules")
else:
    keys = sorted(k for k in vars(_pa) if not k.startswith("__"))
    print("CYC-PKG-PARTIAL -> 在 sys.modules（半成品），业务键=%s" % (keys or "无"))
from _cycpkg.a import X
