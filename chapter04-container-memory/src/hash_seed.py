"""PYTHONHASHSEED 随机化：str/bytes 的哈希盐在每次进程启动时随机生成。
「同一脚本两次运行 hash('a') 不同」——这里用子进程真实取多次运行的值做对比；
再用 PYTHONHASHSEED=0 固定盐对照（两次相同，且与算法相关的值跨版本稳定）。
run_py.py 已从环境剥离 PYTHONHASHSEED，这里再显式剥离一次，保证子进程拿到默认随机化。"""
import os
import subprocess
import sys

# == 1. 随机盐：同一命令、四次独立进程 ==
env = dict(os.environ)
env.pop("PYTHONHASHSEED", None)
cmd = [sys.executable, "-c", "print(hash('a'))"]
print("VERSION\t%s" % sys.version.split()[0])
print("PARENT\t本进程 hash('a') = %d" % hash("a"))
vals = []
for i in range(1, 5):
    v = int(subprocess.run(cmd, capture_output=True, text=True, env=env).stdout.strip())
    vals.append(v)
    print("CHILD\t第%d次独立进程 hash('a') = %d" % (i, v))
distinct = len(set(vals))
print("DISTINCT\t4 个独立进程 → %d 个不同值：每个进程换一次盐 = %s" % (distinct, distinct >= 2))

# == 2. 固定盐对照：PYTHONHASHSEED=0，两次进程相同 ==
env0 = dict(env)
env0["PYTHONHASHSEED"] = "0"
v0 = [subprocess.run(cmd, capture_output=True, text=True, env=env0).stdout.strip()
      for _ in range(2)]
seed0_ok = v0[0] == v0[1]
print("SEED0\tPYTHONHASHSEED=0 第1次进程 = %s" % v0[0])
print("SEED0\tPYTHONHASHSEED=0 第2次进程 = %s（与第1次相同 = %s）" % (v0[1], seed0_ok))

# == 3. int 不参与随机化：hash(42) 恒等于 42 ==
vi = [subprocess.run([sys.executable, "-c", "print(hash(42))"], capture_output=True,
                     text=True, env=env).stdout.strip() for _ in range(2)]
int_ok = vi[0] == vi[1] == "42"
print("INT\tint hash(42) 两次独立进程 = %s / %s（相同 = %s，数值对象不做随机化）" %
      (vi[0], vi[1], vi[0] == vi[1]))
print("SELF-OK\t%d/3" % ((distinct >= 2) + seed0_ok + int_ok))
