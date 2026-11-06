"""importlib.reload 证据链：模块对象原地复用、模块字典原地换内容、
旧引用不更新、旧实例还在别处跑。用环境变量模拟「源码在两次加载之间被改了」。"""
import importlib, os, sys
import _reload_counter
import _reload_target as A_old

# == 1. 第一次加载：TOKEN=v1，抓一批引用
old_inst = A_old.make()
old_cls = A_old.Handler
old_fn = A_old.make
from _reload_target import TOKEN as token_from
print("EXEC-FIRST -> %d" % _reload_counter.N)
print("TOKEN-FIRST -> %s" % A_old.TOKEN)
print("CAPTURED-TOKEN -> %s" % token_from)

# == 2. 「源码变了」：改环境变量后 reload —— 模块体重新执行
os.environ["RT_TOKEN"] = "v2"
A_new = importlib.reload(A_old)
print("EXEC-AFTER -> %d" % _reload_counter.N)
print("MODULE-SAME-OBJ -> %s" % (A_old is A_new))
print("DICT-SAME-OBJ -> %s" % (A_old.__dict__ is A_new.__dict__))
print("TOKEN-NOW -> %s" % A_new.TOKEN)
print("CAPTURED-STILL -> %s" % token_from)

# == 3. 证据链：reload 前后抓的类 / 函数，is 全 False
new_inst = A_new.make()
print("CLS-OLD-IS-NEW -> %s" % (old_cls is A_new.Handler))
print("FN-OLD-IS-NEW -> %s" % (old_fn is A_new.make))
print("INST-CLS-IS-NEW -> %s" % (type(old_inst) is A_new.Handler))
print("OLD-INST-WHO -> %s" % old_inst.who())
print("NEW-INST-WHO -> %s" % new_inst.who())

# == 4. 旧对象还在别处跑：注册表里的旧实例；旧函数读的是被原地更新的模块字典
REG = [old_inst]
print("REG-HOLDS-OLD -> %s" % REG[0].who())
print("OLD-FN-RETURNS -> %s" % old_fn().who())
