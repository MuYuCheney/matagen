
import sys
from io import StringIO
import traceback

def execute_python_code(code: str, output_directory="images") -> str:
    redirected_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = redirected_output
    try:
        # ���� __name__ Ϊ "__main__" ��ģ��ֱ��ִ�нű���Ч��
        exec(code, {"__builtins__": __builtins__, "__name__": "__main__"})
    except Exception:
        traceback.print_exc()  # ��������Ϣ��ӡ���ض���������
    finally:
        sys.stdout = old_stdout
        result = redirected_output.getvalue()
        redirected_output.close()
    return result
