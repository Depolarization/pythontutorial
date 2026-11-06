COUNT = 0
def bump():
    global COUNT
    COUNT += 1
    return COUNT
print("[dualmod] 模块体执行，__name__=%s" % __name__)
if __name__ == "__main__":
    print("[dualmod] 脚本直跑：bump() -> %d" % bump())
    print("[dualmod] 这个实例的 COUNT = %d" % COUNT)
