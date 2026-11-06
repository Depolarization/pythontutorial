# 解法二（import x 用 x.y）：顶部只绑模块对象，属性访问推迟到运行期
import _cycd2_a
Y = "B.Y"
def read_x():
    return _cycd2_a.X
