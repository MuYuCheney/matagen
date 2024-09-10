import sys
from io import StringIO
import traceback
import matplotlib.pyplot as plt
import os
import re
import uuid


def execute_python_code(code: str, output_directory="images") -> dict:
    # 确保输出目录存在
    os.makedirs(output_directory, exist_ok=True)

    # 使用正则表达式查找 plt.show()
    pattern = re.compile(r"plt\.show\(\)")
    matches = pattern.findall(code)
    filename = None
    full_path = None

    if matches:
        # 生成安全的唯一文件名
        filename = f"{uuid.uuid4()}.png"
        safe_filename = ''.join(char for char in filename if char.isalnum() or char in ('-', '_', '.'))
        full_path = os.path.join(output_directory, safe_filename)
        # 替换plt.show()为plt.savefig()，确保使用安全路径
        code = pattern.sub(f"plt.savefig(r'{full_path}')", code)

    redirected_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = redirected_output
    image_path = None
    try:
        # 安全地执行代码
        local_vars = {"plt": plt}
        exec(code, {"__builtins__": __builtins__, "__name__": "__main__", **local_vars})
        if matches and os.path.exists(full_path):
            image_path = full_path
    except Exception as e:
        traceback.print_exc()  # 将错误信息打印到重定向的输出中
    finally:
        sys.stdout = old_stdout
        result = redirected_output.getvalue()
        redirected_output.close()

    # 返回执行结果和图像文件路径（如果存在）
    return {"output": result, "image_path": image_path}
