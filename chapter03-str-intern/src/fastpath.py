"""CPython 的 += 快路径：只在引用计数 == 1 时原地扩容；
多持一个引用就退化成每次全量复制，O(n) 变 O(n^2)。
用 sys.getrefcount 在 += 前一瞬取证，三种写法同规模对拍。
计时 time.perf_counter 取多次最优。纯标准库，只 print。"""
import sys
import time

SEP = '-' * 62
N = 20000
PARTS = ['片段%05d的文本内容' % i for i in range(N)]   # 每段 12 码点（中文，内部 2 字节/格）


def fast():
    s = ''
    for p in PARTS:
        s += p
    return s


def shared():
    s = ''
    keep = None
    for p in PARTS:
        keep = s                       # 多持一个引用，refcount 变 2
        s += p
    return s


def plain_plus():
    s = ''
    for p in PARTS:
        s = s + p                      # 结果立刻写回同一变量：同样吃到快路径
    return s


def bench(fn, rep=5):
    best = float('inf')
    for _ in range(rep):
        t0 = time.perf_counter()
        r = fn()
        best = min(best, time.perf_counter() - t0)
    return best, r


def rc_snapshot(hold):
    """在 += 执行前一刻抓 refcount；跳过第 1 轮（起始串可能是 immortal 单例）。"""
    s = ''.join(['a', 'b'])            # 运行期新造，refcount 干净
    keep = None
    rcs = []
    for i in range(3):
        if hold:
            keep = s
        if i >= 1:
            rcs.append(sys.getrefcount(s))
        s += '尾%d' % i
    return rcs


print('== += 快路径：refcount==1 才原地扩容 ==')
print('PY 版本 -> %s' % sys.version.split()[0])
FULL = ''.join(PARTS)
print('FP size -> %d 段 x %d 码点（中文 内部 2 字节/格）| 成品 %d 码点 / %d KB'
      % (N, len(PARTS[0]), len(FULL), len(FULL.encode()) // 1024))

print(SEP)
print('== 三种写法同规模对拍（5 次取最优）==')
t_fast, r1 = bench(fast)
t_shared, r2 = bench(shared)
t_plain, r3 = bench(plain_plus)
print('ROW fast -> %.4f s | s += p，循环里只有局部变量持有它' % t_fast)
print('ROW shared -> %.4f s | 每轮先 keep = s 多持一个引用' % t_shared)
print('ROW plain -> %.4f s | s = s + p，结果立刻写回也吃快路径' % t_plain)
print('EQ results -> %s | 三种写法结果一致' % (r1 == r2 == r3))
print('RATIO shared/fast -> %.0fx' % (t_shared / t_fast))

print(SEP)
print('== refcount 取证：+= 前一刻，多持引用的那份恰好 +1 ==')
rf = rc_snapshot(False)
rs = rc_snapshot(True)
print('RC fast -> %s' % rf)
print('RC shared -> %s' % rs)
print('RC delta -> +%d | 多持引用的那份恰好 +1' % (rs[0] - rf[0]))
print('RC note -> 绝对值随解释器浮动（3.14 的 LOAD_FAST 不再加引用），相对差 +1 才是信号')

print(SEP)
print('== 规模加倍对照：快路径线性，退化二次方 ==')
for n in (5000, 10000, 20000):
    parts_n = PARTS[:n]

    def f():
        s = ''
        for p in parts_n:
            s += p
        return s

    def g():
        s = ''
        keep = None
        for p in parts_n:
            keep = s
            s += p
        return s

    tf, _ = bench(f, rep=3)
    tg, _ = bench(g, rep=3)
    print('SCALE N%d -> 快 %.4f s | 退化 %.4f s | %.0fx' % (n, tf, tg, tg / tf))
print('CC fast -> 原地扩容摊还 O(n)；多一个引用 -> str 不可变只能全量复制，O(n^2)')
