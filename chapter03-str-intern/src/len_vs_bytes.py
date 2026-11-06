"""len 数的是码点不是字节：len / 三种编码字节数 / UTF-8 编解码往返。
含 utf-16 代理对（码元 != 码点）与组合字符（码点 != 用户感知字符）两个坑。
纯标准库，只 print。"""
import sys

SEP = '-' * 62
BIG = chr(0x20000)
SAMPLES = [
    ('ascii', 'abc', '纯 ASCII'),
    ('kana', 'あああ', '日文假名'),
    ('astral', BIG, '扩展B区单字 U+20000'),
    ('mixed', 'aあ' + BIG, '三种混排'),
    ('combine', 'e\u0301', 'e + 组合尖音符'),
]


def widths(s):
    return tuple(len(s.encode(e)) for e in ('utf-8', 'utf-16-le', 'utf-32-le'))


print('== len 数码点，encode 数字节 ==')
print('PY 版本 -> %s' % sys.version.split()[0])

print(SEP)
print('== 同一批串：len（码点）vs 三种编码的字节数 ==')
for name, s, note in SAMPLES:
    u8, u16, u32 = widths(s)
    print('LN %s -> len=%d 码点 | utf-8 %d B | utf-16-le %d B | utf-32-le %d B | %s'
          % (name, len(s), u8, u16, u32, note))

print(SEP)
print('== utf-16 代理对：1 个码点占 2 个码元 ==')
u16 = BIG.encode('utf-16-le')
print('SU len -> len(%r) = %d 码点' % ('U+20000', len(BIG)))
print('SU bytes -> %s | %d B = %d 个 16 位码元' % (u16.hex(' '), len(u16), len(u16) // 2))
print('SU units -> %s + %s | 高位代理 + 低位代理' % (u16[:2].hex(), u16[2:].hex()))
print('SU other -> utf-8 %d B / utf-32-le %d B | utf-8 用 4 字节，utf-32 用 1 格'
      % (len(BIG.encode('utf-8')), len(BIG.encode('utf-32-le'))))

print(SEP)
print('== 编解码往返：decode(encode(s)) == s ==')
for name, s, _ in SAMPLES:
    oks = ['%s:%s' % (e, s.encode(e).decode(e) == s)
           for e in ('utf-8', 'utf-16-le', 'utf-32-le')]
    print('RT %s -> %s' % (name, ' '.join(oks)))
print('RT all -> %s | 全部样本 x 三种编码'
      % all(s.encode(e).decode(e) == s for _, s, _ in SAMPLES
            for e in ('utf-8', 'utf-16-le', 'utf-32-le')))

print(SEP)
print('== 往返的边界：非法字节当场翻脸 ==')
try:
    b'\xff\xfe\x41'.decode('utf-8')
except UnicodeDecodeError as e:
    print('BF strict -> UnicodeDecodeError: %s' % e.reason)
print('BF replace -> %r | errors=replace 换成占位符不报错' % b'\xff\xfe\x41'.decode('utf-8', errors='replace'))
print('CC len 是码点数：utf-8 里 1~4 字节、utf-16 里 1~2 码元、utf-32 恒 1 格，len 全都不管')
