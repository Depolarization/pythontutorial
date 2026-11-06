"""双实例问题：同一份 .py 被当脚本直跑一次、又被 import 一次 = 两个独立模块对象。
if __name__ == "__main__" 存在的唯一理由就是这个。"""
import os, pathlib, runpy, subprocess, sys
import _dualmod as dm

# == 1. 先 import 一次：helper 以 _dualmod 身份进 sys.modules
print("PROBE-NAME -> %s" % __name__)              # 探针自己以 __main__ 身份在跑
dm.bump(); dm.bump()
print("IMPORTED-COUNT -> %d" % dm.COUNT)
import _dualmod as dm2
print("DOUBLE-IMPORT-SAME -> %s" % (dm is dm2))

# == 2. 真实场景：独立子进程把同一份文件当脚本直跑
here = pathlib.Path(__file__).resolve().parent
r = subprocess.run([sys.executable, "-X", "utf8", str(here / "_dualmod.py")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   env=dict(os.environ, PYTHONIOENCODING="utf-8"))
print("--- 子进程 python _dualmod.py ---")
sys.stdout.write(r.stdout)
lines = r.stdout.splitlines()
print("SCRIPT-NAME -> %s" % next(l for l in lines if "__name__=" in l).split("__name__=")[1].strip())
print("SCRIPT-COUNT -> %s" % next(l for l in lines if "COUNT =" in l).rsplit("=", 1)[1].strip())

# == 3. runpy 在本进程内再执行同一份文件：同一进程里的第二个实例
g = runpy.run_path(str(here / "_dualmod.py"), run_name="__main__")
print("RUNPY-NAME -> %s" % g["__name__"])
print("RUNPY-COUNT -> %d" % g["COUNT"])
print("IMPORTED-STILL -> %d" % dm.COUNT)
print("STATE-NOT-SHARED -> %s" % (dm.COUNT != g["COUNT"]))
