"""字面量 intern 规则：标识符形状的编译期常量自动进 intern 表；
运行期拼接出来的串不 intern，要手动 sys.intern。
用两个函数、两个 exec 编译单元、运行期拼接三方对拍 is / ==。
纯标准库，只 print。"""
import sys

SEP = '-' * 62


def lit_ident_a():
    return 'py_str_3'                    # 标识符形状（字母数字下划线）


def lit_ident_b():
    return 'py_str_3'


def lit_space_a():
    return 'hello world'                 # 带空格，不是标识符形状


def lit_space_b():
    return 'hello world'


print('== 字面量 intern：谁能自动进 intern 表 ==')
print('PY 版本 -> %s' % sys.version.split()[0])

print(SEP)
print('== 同一模块里的两个函数：编译单元内常量合并 ==')
print('IN ident-samemod -> %s | 标识符形状字面量，两个函数同一对象' % (lit_ident_a() is lit_ident_b()))
print('IN space-samemod -> %s | 带空格字面量同模块也同对象：这是常量合并，不是 intern 的证据'
      % (lit_space_a() is lit_space_b()))

print(SEP)
print('== 两个独立编译单元：intern 表是全局的，常量合并不是 ==')
ns1, ns2, ns3, ns4 = {}, {}, {}, {}
exec(compile("v = 'py_str_3'", '<单元1>', 'exec'), ns1)
exec(compile("v = 'py_str_3'", '<单元2>', 'exec'), ns2)
exec(compile("v = 'hello world'", '<单元3>', 'exec'), ns3)
exec(compile("v = 'hello world'", '<单元4>', 'exec'), ns4)
print('IN ident-crossunit -> %s | 标识符形状：进了全局 intern 表，跨单元同对象' % (ns1['v'] is ns2['v']))
print('IN space-crossunit -> %s | 带空格：没进 intern 表，各造各的对象' % (ns3['v'] is ns4['v']))

print(SEP)
print('== 运行期拼接：内容相同、身份不同 ==')
head = 'py_'
tail = 'str_3'
run1 = head + tail                      # 运行期拼接，编译器不在场
run2 = head + tail
print('RT eq -> %s | run1 == run2，内容一样' % (run1 == run2))
print('RT is -> %s | run1 is run2，但身份不同' % (run1 is run2))
print('RT is-literal -> %s | run1 is 字面量：内容一样也没用，运行期不查 intern 表'
      % (run1 is lit_ident_a()))

print(SEP)
print('== sys.intern：手动把串放进 intern 表 ==')
canon1 = sys.intern(run1)
canon2 = sys.intern(run2)
print('IA intern-two -> %s | intern(run1) is intern(run2)，收拢为同一对象' % (canon1 is canon2))
print('IA intern-literal -> %s | intern 后和字面量是同一个对象：同一内容只有一个真身'
      % (canon1 is lit_ident_a()))
w1 = sys.intern('hello world')
w2 = sys.intern('hello world')
print('IA intern-space -> %s | intern 不挑形状，谁都能手动进' % (w1 is w2))

print(SEP)
print('== intern 的实际收益：1 万个重复 token 收拢成 1 个对象 ==')
tokens = ['status_code_%d' % (i % 10) for i in range(10000)]
ids_before = len(set(map(id, tokens)))
interned = [sys.intern(t) for t in tokens]
ids_after = len(set(map(id, interned)))
print('TK before -> %d 个不同 id（1 万个内容重复的串对象）' % ids_before)
print('TK after -> %d 个不同 id（intern 后只剩 10 个真身）' % ids_after)
saved = sum(sys.getsizeof(t) for t in tokens) - sum(sys.getsizeof(t) for t in set(interned))
print('TK saved -> 约 %d KB 字符串本体' % (saved // 1024))
print('CC 规则 -> 标识符形状的字面量编译期自动 intern；运行期拼接的串要手动 sys.intern')
