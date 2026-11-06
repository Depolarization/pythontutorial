# 选题5 探针D：装饰器/工厂的闭包持有大对象 —— tracemalloc 前后对比实测内存滞留
# 纯标准库；只 print 不写文件；约定「KEY -> 值」行供网页取数
import gc, sys, tracemalloc

print("EXPL", "->", sys.version.split()[0])
BIGN = 50_000
ROUNDS = 20

# == A. 闭包抓住大对象：用完即弃也放不掉 ==
def handler_for(data):
    def handle(key):
        return len(data)          # 闭包引用 data —— 整份大对象被留在 cell 里
    return handle

tracemalloc.start()
keepers = []
for _ in range(ROUNDS):
    data = list(range(BIGN))      # 调用方视角里「用完就丢」的大对象
    keepers.append(handler_for(data))
gc.collect()
cur1, _peak1 = tracemalloc.get_traced_memory()
tracemalloc.stop()
print("RETAIN with bytes", "->", cur1)
print("RETAIN with MB", "->", round(cur1 / 1048576, 1))

# == B. 对照：闭包只留摘要（一个 int），大对象当场回收 ==
def handler_sum(n):
    def handle(key):
        return n
    return handle

tracemalloc.start()
keepers2 = []
for _ in range(ROUNDS):
    data = list(range(BIGN))
    n = len(data)                 # 只留摘要
    keepers2.append(handler_sum(n))
    del data
gc.collect()
cur2, _peak2 = tracemalloc.get_traced_memory()
tracemalloc.stop()
print("RETAIN without bytes", "->", cur2)
print("RETAIN without KB", "->", round(cur2 / 1024, 1))
print("RETAIN ratio", "->", round(cur1 / cur2, 1))

# == C. 滞留证据：cell 里就是那份 data 本尊 ==
h = handler_for([10, 20, 30])
print("CLOSURE count", "->", len(h.__closure__))
print("CLOSURE type", "->", type(h.__closure__[0].cell_contents).__name__)
print("CLOSURE 内容", "->", h.__closure__[0].cell_contents)
print("CLOSURE handle 调用", "->", h("k"))
