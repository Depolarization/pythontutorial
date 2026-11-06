# 解法一（延迟 import）：把 from _cycd1_a import X 挪进函数体，调用那一刻 a 早已初始化完
Y = "B.Y"
def late_x():
    from _cycd1_a import X
    return X
