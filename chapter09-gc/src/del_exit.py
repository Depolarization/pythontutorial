"""__del__ 与解释器退出的经典崩溃：全局名先被清，__del__ 后跑。
两种触发都实测：手动删名/置 None（确定性复现）与真实退出（留守对象）。
全程 try/except 捕获后打印，保证退出码 0。"""
import sys

print("PY " + ".".join(map(str, sys.version_info[:3])))

# == 1. 机制复现：全局名没了，__del__ 里还在用 ==
LOG = ["全局日志（加载时创建）"]


class Flusher:
    def __del__(self):
        try:
            LOG.append("收尾时写一条")           # 摸全局名
            print("DEL1  全局 LOG 还在 -> %r" % (LOG,))
        except Exception as e:
            print("DEL1  崩溃捕获 -> %s: %s" % (type(e).__name__, e))


f = Flusher()
print("STEP1 对象已创建；现在 del LOG（模拟「全局名先没了」）")
del LOG
del f                                    # __del__ 此刻触发 → 摸不到 LOG
print("STEP1 del f 已执行，上面一行就是捕获结果")

# == 2. 模拟「退出时全局被置 None」——经典 TypeError ==
REPORT = print                            # 现实里这是 logger / 连接 / 文件对象


class Sentry:
    def __del__(self):
        try:
            REPORT("进程收尾，写最后一条日志")
        except Exception as e:
            print("DEL2  崩溃捕获 -> %s: %s" % (type(e).__name__, e))


s = Sentry()
print("STEP2 全局 REPORT 先被置 None（解释器退出时全局就是先没的）")
REPORT = None
del s                                     # __del__ 触发 → None 不可调用
print("STEP2 del s 已执行，上面一行就是捕获结果")

# == 3. 真实退出：留守对象，__del__ 在模块拆除后触发 ==
LAST = Flusher()
print("STEP3 LAST 留守到解释器退出——它的 __del__ 将在模块拆除后触发")
print("DONE  主程序结束，之后进入解释器退出流程（本探针退出码恒为 0）")
