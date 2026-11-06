# pythontutorial —— Python 底层原理实战教程系列

一系列围绕 **Python** 的底层原理实战教程。每一章是一个独立、可运行的专题，配有核心 Python 源码与一段讲解视频。
**章节文件夹以核心 Python 源码为主**（GitHub 仅作为视频的源码附件托管，构建/录制等流水线不入库）；
每章附 `dual/` —— 同一份探针在 CPython 3.14.7（主）与 3.13.14（对照）两个解释器上的原始输出，视频里引用的每个数字都能在其中找到原文。

## 章节

| # | 标题 | 一句话简介 | 视频 | 源码 |
| --- | --- | --- | --- | --- |
| 1 | 257 is 257 时真时假 —— 小整数缓存、常量折叠与 is 的雷区 | 小整数缓存 -5..256、常量折叠与编译单元边界、SyntaxWarning、dis 常量槽位、任意精度整数 30 位台阶；5 份探针 × 双解释器 82 行原始输出逐行对拍。 | 见 B 站（搜索标题） | [chapter01-int-cache/](chapter01-int-cache/) |
| 2 | 0.1 + 0.2 不等于 0.3 只是开始 —— float 三坑与精确数值方案 | 0.1 + 0.2 的二进制真相与 float 存储、round 两坑、floor 整除与取模、Decimal / Fraction / 整数分三件套、nan 的短路与 isnan；双解释器实测。 | 见 B 站（搜索标题） | [chapter02-float-pitfalls/](chapter02-float-pitfalls/) |
| 3 | 循环 += 突然慢百倍 —— str 编码、intern 与拼接快路径 | PEP 393 格宽与头部账本、len 与编码字节、intern 规则、`+=` 快路径与 refcount、六种拼接横评；双解释器对账。 | 见 B 站（搜索标题） | [chapter03-str-intern/](chapter03-str-intern/) |
| 4 | list 超配与 dict 有序 —— 容器内存布局与三种拷贝语义 | list 超配公式与头删 O(n)、deque 对照、dict 有序与分裂表、哈希随机化、a[:] / copy / deepcopy 的拷贝语义矩阵。 | 见 B 站（搜索标题） | [chapter04-container-memory/](chapter04-container-memory/) |
| 5 | 循环里的 lambda 全打印同一个数 —— 可变默认参数与 late binding | 默认值只求值一次、None 哨兵、闭包晚绑定与 cell 证据、三种修复实测、作用域泄漏与闭包内存滞留。 | 见 B 站（搜索标题） | [chapter05-default-args/](chapter05-default-args/) |
| 6 | property 也有压不住的时候 —— 描述符、MRO 与 super() | 五层属性查找优先级、data / non-data 描述符压制、property 子类坑、C3 与 MRO 报错、零参 super() 的 cell、`__slots__` 陷阱与 tracemalloc 真账、五路计时。 | 见 B 站（搜索标题） | [chapter06-attr-lookup/](chapter06-attr-lookup/) |
| 7 | 被吞掉的 StopIteration —— 迭代器协议、生成器与 PEP 479 | 迭代器一次性、zip 复用两坑、for 的静默截断、被吞掉的 return 值、PEP 479、next default 边界、生成器收尾与内存账。 | 见 B 站（搜索标题） | [chapter07-iterator/](chapter07-iterator/) |
| 8 | partially initialized module —— 循环导入、reload 与自定义 loader | sys.modules 缓存与取物时机、循环导入半成品现场、双实例 `__main__`、reload 证据链、内存 loader 与 zipimport、包 `__init__` 顺序。 | 见 B 站（搜索标题） | [chapter08-import/](chapter08-import/) |
| 9 | del 之后内存没降 —— 引用计数、循环引用与 tracemalloc 抓泄漏 | 引用计数即时回收、分代阈值与停顿、循环引用抓环、RSS 与分配器、`__del__` 退出崩溃、弱引用破泄漏、tracemalloc 快照 diff 定位行号。 | 见 B 站（搜索标题） | [chapter09-gc/](chapter09-gc/) |
| 10 | 开 8 个线程为什么不快 —— GIL、竞态与 free-threading | GIL 到底锁什么、竞态实测、切换粒度、CPU 密集的线程与进程、I/O 密集主场、free-threading 构建对拍、append 陷阱与选型。 | 见 B 站（搜索标题） | [chapter10-gil/](chapter10-gil/) |

## 适合谁

- 被 `257 is 257` 时真时假、`is` 与 `==` 的边界绕晕，想知道小整数缓存与编译单元到底怎么划界的人；
- 被 `0.1 + 0.2` 坑过，想搞清楚 IEEE 754 存储、round 规则与金额计算该用什么方案的人；
- 想弄明白 str 的编码格宽、intern、`+=` 快路径与拼接选型的人；
- 对 list 超配、dict 有序、哈希随机化与深浅拷贝边界感兴趣的人；
- 踩过可变默认参数、闭包 late binding、描述符与 MRO、迭代器一次性、循环导入、GC 与 GIL 的人；
- 想看「确定性网页渲染 + 配音 + 逐帧录制」怎么做技术讲解视频的人。

## 约定

- 每章文件夹各自独立，只含核心 Python 源码与 `dual/` 原始输出；视频与封面随章节在 B 站发布，不在仓库内。
- 全部探针只用标准库，无第三方依赖；CPython 3.14.7 为主、3.13.14 为对照，`dual/<脚本>.py313.txt` / `.py314.txt` 是对应版本的原样输出。
- 入口：`cd <chapter>/src` 后直接 `python <脚本>.py`。第 8 章的 `_pkgdemo/`、`_pkgdemo2/`、`_cycpkg/`、`_memdemo.zip` 是循环导入、包执行顺序与 zipimport 实验所需的样例，请保留目录结构。
- 耗时、内存与 `getrefcount` 读数跟解释器版本和机器走，视频里的倍率只作同机对比；换机器或换构建请重跑，别拿本仓库的数字当基准。
- `dual/` 是录制时的原文；解释器打了补丁后报错文案或数字可能变化，以你自己跑出的输出为准。

## 许可证

见 [LICENSE](LICENSE)。
