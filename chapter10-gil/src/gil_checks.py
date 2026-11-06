# -*- coding: utf-8 -*-
"""解释器自查：GIL 相关接口、切换粒度、机器核数、本机有没有 free-threaded 构建，
以及 x += 1 这条语句到底被编译成哪几条字节码（竞态的地基）。
只 print，不写文件。
"""
import dis
import os
import pathlib
import sys
import sysconfig

X = 0


def bump():
    global X
    X += 1


def main():
    print("VERSION\t%s" % sys.version.replace("\n", " "))
    print("EXE\t%s" % sys.executable)
    print("IMPL\t%s %s" % (sys.implementation.name, ".".join(map(str, sys.implementation.version))))

    has_api = hasattr(sys, "_is_gil_enabled")
    print("HAS_GIL_API\t%s\t（3.13 起才有这个接口）" % has_api)
    print("GIL_ENABLED\t%s" % (sys._is_gil_enabled() if has_api else "接口不存在"))
    print("SWITCH\t%.4f ms" % (sys.getswitchinterval() * 1000))
    print("CORES\t%d" % os.cpu_count())
    conf = sysconfig.get_config_var("Py_GIL_DISABLED")
    print("BUILD_FLAG\tPy_GIL_DISABLED=%s\t（编译期是否关掉 GIL）" % conf)

    # 本机有没有 free-threaded 解释器：先看默认构建旁边，再看临时目录里的便携版
    here = pathlib.Path(sys.executable).parent
    beside = [here / n for n in ("python3.14t.exe", "python314t.exe", "python3.13t.exe")]
    found_beside = [str(p) for p in beside if p.exists()]
    print("FT_BESIDE\t%s" % ("找到 " + "; ".join(found_beside) if found_beside
                             else "没找到（默认构建目录里没有 t 版解释器）"))
    portable = pathlib.Path(r"D:/Agent/tmp/py-topic10/ft/python3.14t.exe")
    print("FT_PORTABLE\t%s" % (("找到 " + str(portable)) if portable.exists()
                                else "没找到（未下载便携版）"))

    print("DIS_BEGIN")
    for line in dis.Bytecode(bump).dis().splitlines():
        print("DIS\t" + line)
    print("DIS_END")
    print("NOTE\t计数器和写回分属不同字节码，中间是一个可以切走的空隙；"
          "GIL 只保证单条字节码不被打断")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
