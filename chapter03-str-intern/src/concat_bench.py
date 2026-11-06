"""六种拼接写法横评：+= 快路径 / list+join / io.StringIO / f-string / %-format / reduce。
三种规模（5千/1万/2万段）计时画曲线，tracemalloc 量 2 万段时的峰值内存。
计时 time.perf_counter 取 3 次最优。纯标准库，只 print。"""
import io
import sys
import time
import tracemalloc
from functools import reduce
from operator import add

SEP = '-' * 62
FULL = 20000
SIZES = (5000, 10000, FULL)
PARTS = ['片段%05d的文本内容' % i for i in range(FULL)]
EXPECTED = ''.join(PARTS)


def plus_eq(parts):
    s = ''
    for p in parts:
        s += p
    return s


def join_list(parts):
    buf = []
    for p in parts:
        buf.append(p)
    return ''.join(buf)


def string_io(parts):
    b = io.StringIO()
    for p in parts:
        b.write(p)
    return b.getvalue()


def fstring_acc(parts):
    s = ''
    for p in parts:
        s = f'{s}{p}'
    return s


def percent_acc(parts):
    s = ''
    for p in parts:
        s = '%s%s' % (s, p)
    return s


def reduce_add(parts):
    return reduce(add, parts, '')


METHODS = [
    ('pluseq',   '+= 就地拼接', plus_eq),
    ('join',     'list+join', join_list),
    ('stringio', 'io.StringIO', string_io),
    ('fstring',  'f-string 累加', fstring_acc),
    ('percent',  '% 累加', percent_acc),
    ('reduce',   'reduce(add)', reduce_add),
]

print('== 六种拼接横评：2 万段文本 ==')
print('PY 版本 -> %s' % sys.version.split()[0])
print('CB data -> %d 段 x %d 码点（中文 内部 2 字节/格）| 成品 %d 码点 / %d KB'
      % (FULL, len(PARTS[0]), len(EXPECTED), len(EXPECTED.encode()) // 1024))

print(SEP)
print('== 耗时曲线：三种规模各 3 次取最优 ==')
for key, label, fn in METHODS:
    bests = []
    for n in SIZES:
        parts = PARTS[:n]
        best = float('inf')
        for _ in range(3):
            t0 = time.perf_counter()
            r = fn(parts)
            best = min(best, time.perf_counter() - t0)
        bests.append(best)
    ok = (r == EXPECTED)
    print('TN %s 5000 -> %.4f s' % (key, bests[0]))
    print('TN %s 10000 -> %.4f s' % (key, bests[1]))
    print('TN %s 20000 -> %.4f s' % (key, bests[2]))
    print('ROW %s -> %s | 2万段 %7.4f s | 结果正确 %s' % (key, label, bests[2], ok))

print(SEP)
print('== tracemalloc 峰值：拼 2 万段时最多同时压着多少内存 ==')
for key, label, fn in METHODS:
    tracemalloc.start()
    r = fn(PARTS)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    print('PK %s -> %8.1f KB | %s，成品 %d KB' % (key, peak / 1024, label, len(r.encode()) // 1024))

print(SEP)
print('== 增长倍率：段数 x4（5千->2万），耗时 x几 ==')
for key, label, fn in METHODS:
    t0 = time.perf_counter()
    fn(PARTS[:5000])
    t_small = time.perf_counter() - t0
    t0 = time.perf_counter()
    fn(PARTS)
    t_big = time.perf_counter() - t0
    print('GR %s -> x%.0f | 线性应约 x4，二次方应约 x16' % (key, t_big / max(t_small, 1e-6)))
print('CC join-stringio -> 一次到位线性；fstring-percent-reduce -> 每步都造新串，天然 O(n^2)')
