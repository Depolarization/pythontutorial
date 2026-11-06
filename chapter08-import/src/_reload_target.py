import os
import _reload_counter
_reload_counter.N += 1
TOKEN = os.environ.get("RT_TOKEN", "v1")
print("[reload_target] 模块体第 %d 次执行，TOKEN=%s" % (_reload_counter.N, TOKEN))
class Handler:
    def __init__(self):
        self.token = TOKEN          # 创建那一刻的 TOKEN 烤进实例
    def who(self):
        return "Handler@" + self.token
def make():
    return Handler()
