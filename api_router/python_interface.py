import sys
from io import StringIO
import traceback
import matplotlib.pyplot as plt
import os
import re
import uuid


def execute_python_code(code: str, output_directory="images") -> dict:
    # ȷ�����Ŀ¼����
    os.makedirs(output_directory, exist_ok=True)

    # ʹ��������ʽ���� plt.show()
    pattern = re.compile(r"plt\.show\(\)")
    matches = pattern.findall(code)
    filename = None
    full_path = None

    if matches:
        # ���ɰ�ȫ��Ψһ�ļ���
        filename = f"{uuid.uuid4()}.png"
        safe_filename = ''.join(char for char in filename if char.isalnum() or char in ('-', '_', '.'))
        full_path = os.path.join(output_directory, safe_filename)
        # �滻plt.show()Ϊplt.savefig()��ȷ��ʹ�ð�ȫ·��
        code = pattern.sub(f"plt.savefig(r'{full_path}')", code)

    redirected_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = redirected_output
    image_path = None
    try:
        # ��ȫ��ִ�д���
        local_vars = {"plt": plt}
        exec(code, {"__builtins__": __builtins__, "__name__": "__main__", **local_vars})
        if matches and os.path.exists(full_path):
            image_path = full_path
    except Exception as e:
        traceback.print_exc()  # ��������Ϣ��ӡ���ض���������
    finally:
        sys.stdout = old_stdout
        result = redirected_output.getvalue()
        redirected_output.close()

    # ����ִ�н����ͼ���ļ�·����������ڣ�
    return {"output": result, "image_path": image_path}
