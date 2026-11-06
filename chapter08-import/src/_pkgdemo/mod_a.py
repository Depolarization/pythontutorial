from . import mod_b
print("[_pkgdemo.mod_a] 模块体执行")
NAME = "mod_a"
def b_name():
    return mod_b.NAME
