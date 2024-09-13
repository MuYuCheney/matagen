
import sys
from io import StringIO
import traceback

def execute_python_code(code: str, output_directory="images") -> str:
    redirected_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = redirected_output
    try:
        # 设置 __name__ 为 "__main__" 来模拟直接执行脚本的效果
        exec(code, {"__builtins__": __builtins__, "__name__": "__main__"})
    except Exception:
        traceback.print_exc()  # 将错误信息打印到重定向的输出中
    finally:
        sys.stdout = old_stdout
        result = redirected_output.getvalue()
        redirected_output.close()
    return result
