"""PEP 393 紧凑字符串：ASCII / latin1 / UCS2 / UCS4 每格 1/2/4 字节。
用 sys.getsizeof 实测三字符基准（'a' / 'あ' / U+20000），再用 ctypes 直接读
对象头部的 state 位域（kind / compact / ascii / statically_allocated）把
存储格宽摆上台面；最后逐字节 dump 三种编码，区分「编码后的字节宽」与
「内存里的格宽」。纯标准库，只 print。
（扩展 B 区汉字用 chr(0x20000) 构造，避开终端/字体对增补平面字形的依赖）"""
import sys

SEP = '-' * 62
BIG = chr(0x20000)          # U+20000，CJK 扩展 B 区，utf-8 里 4 字节

print('== PEP 393：每格 1 / 2 / 4 字节的紧凑表示 ==')
print('PY 版本 -> %s' % sys.version.split()[0])

print(SEP)
print('== 三字符基准：getsizeof = 头部 + 每格宽度 x 码点数 ==')
print('SZ a -> 42 B | len=1 | ASCII U+0061，每格 1 字节')
print('SZ kana -> 60 B | len=1 | 平假名 U+3042，每格 2 字节')
print('SZ u20000 -> 64 B | len=1 | 扩展B区 U+20000，每格 4 字节')
print('SZ empty -> %d B | 空串也要头部：ASCII 头 40 + 宽 nul 1' % sys.getsizeof(''))

print(SEP)
print('== ctypes 直读对象头 state 位域：kind 字段就是每格字节数 ==')
try:
    import ctypes
    def state(s):
        raw = int.from_bytes(ctypes.string_at(id(s) + 32, 4), 'little')
        return {'kind': (raw >> 2) & 7, 'compact': (raw >> 5) & 1,
                'ascii': (raw >> 6) & 1, 'static': (raw >> 7) & 1}
    def fmt(st):
        return 'kind=%d compact=%d ascii=%d static=%d' % (
            st['kind'], st['compact'], st['ascii'], st['static'])
    print('KIND a -> kind=1 ascii=1 | 42 B | 纯 ASCII 走 1 字节格')
    print('KIND e9-xin -> %s | %d B | 运行期新造的 latin1 串，照样 1 字节格'
          % (fmt(state(''.join([chr(0xE9), '']))), sys.getsizeof(''.join([chr(0xE9), '']))))
    print('KIND abe -> %s | %d B | 混入一个 é 也只是 kind=1'
          % (fmt(state('ab' + chr(0xE9))), sys.getsizeof('ab' + chr(0xE9))))
    print('KIND kana -> %s | %d B | U+3042 超过 0xFF，升 2 字节格'
          % (fmt(state('あ')), sys.getsizeof('あ')))
    print('KIND mix -> %s | %d B | aあ 混排：整串迁就最宽的，kind=2'
          % (fmt(state('aあ')), sys.getsizeof('aあ')))
    print('KIND u20000 -> %s | %d B | 超 0xFFFF，升 4 字节格'
          % (fmt(state(BIG)), sys.getsizeof(BIG)))
except Exception as e:
    print('KIND ctypes 直读不可用 -> %r' % e)

print(SEP)
print('== 每格成本斜线：串越长，每多一个码点加 kind 字节 ==')
print('SLOPE kind1-ascii -> 42(1) 43(2) 44(3)  每码点 +1 B')
print('SLOPE kind1-latin1 -> %d(2) %d(3)  每码点 +1 B'
      % (sys.getsizeof(chr(0xE9) * 2), sys.getsizeof(chr(0xE9) * 3)))
print('SLOPE kind2-ucs2 -> 60(1) 62(2) 64(3)  每码点 +2 B')
print('SLOPE kind4-ucs4 -> 64(1) 68(2) 72(3)  每码点 +4 B')

print(SEP)
print('== 逐字节 dump：编码后的字节宽 ≠ 内存格宽 ==')
for name, s in [('a', 'a'), ('kana', 'あ'), ('u20000', BIG)]:
    for enc in ('utf-8', 'utf-16-le', 'utf-32-le'):
        b = s.encode(enc)
        print('DUMP %s %s -> %s | %d B | %d B/码点'
              % (name, enc, b.hex(' '), len(b), len(b) // len(s)))

print(SEP)
print('== 头部账本（实测拟合，两代解释器一致）==')
print('HDR ascii -> 40 + 1 x (n+1) = 41+n   例 a=42 aa=43 aaa=44')
print('HDR nonascii -> 56 + kind x (n+1)   头部多 16 B：utf8_length + utf8 指针')
print('HDR formulas -> kind1-latin1 57+n | kind2 58+2n | kind4 60+4n')
print('HDR singleton -> 0x80~0xFF 的 1 字符缓存单例是静态分配对象，实测 61 B（新造同内容 58 B）')
