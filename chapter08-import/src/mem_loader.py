"""MetaPathFinder 自定义 loader：模块从内存字典里来；sys.path 直接指向 zip。
全程不落盘，_memdemo.zip 是预先放好的夹具。"""
import importlib, importlib.util, pathlib, sys, types

# == 1. 最直白的「字典模块」：直接把模块对象塞进 sys.modules
fake = types.ModuleType("fake_mod")
fake.GREET = "hello from dict"
def f():
    return "fake_mod.f()"
fake.f = f
sys.modules["fake_mod"] = fake
import fake_mod                      # import 第一步查 sys.modules，直接命中
print("FAKE-HELLO -> %s" % fake_mod.GREET)
print("FAKE-CALL -> %s" % fake_mod.f())
print("FAKE-SAME -> %s" % (fake_mod is fake))

# == 2. MetaPathFinder + Loader：源码放在字典里，import 时现场编译
SOURCE = {
    "virt_mod": (
        "X = 42\n"
        "def square(v):\n"
        "    return v * v\n"
        "print('[virt_mod] 模块体执行，源码来自内存字典')\n"
    )
}
class MemFinder:
    def find_spec(self, fullname, path=None, target=None):
        if fullname in SOURCE:
            return importlib.util.spec_from_loader(fullname, MemLoader(fullname))
        return None
class MemLoader:
    def __init__(self, name):
        self.name = name
    def create_module(self, spec):
        return None                  # 用默认模块对象
    def exec_module(self, module):
        module.__file__ = "<mem:%s>" % self.name
        code = compile(SOURCE[self.name], "<mem:%s>" % self.name, "exec")
        exec(code, module.__dict__)
sys.meta_path.insert(0, MemFinder())
import virt_mod
print("VIRT-X -> %d" % virt_mod.X)
print("VIRT-SQUARE -> %d" % virt_mod.square(7))
print("VIRT-FILE -> %s" % virt_mod.__file__)
print("VIRT-IN-MODULES -> %s" % ("virt_mod" in sys.modules))

# == 3. sys.path 直接指向一个 zip 文件：zipimport 接管
sys.meta_path.pop(0)                 # 拆掉 finder，不影响 zip 演示
zpath = str(pathlib.Path(__file__).resolve().with_name("_memdemo.zip"))
sys.path.insert(0, zpath)
import zipmod
print("ZIP-WHO -> %s" % zipmod.WHO)
print("ZIP-GREET -> %s" % zipmod.greet())
print("ZIP-FILE -> %s" % zipmod.__file__)
