from server.identity_verification.decryption import decrypt_string
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from server.utils import find_env_file


# 从加密字符串中提取有效的 API 密钥和类型。
def get_key_info(api_key: str) -> tuple:
    """
    从加密字符串中提取有效的 API 密钥和类型。

    :param api_key: 加密的 API 密钥字符串
    :return: 提取的 API 密钥和状态的元组，如果无效则返回 (None, None)
    """
    try:
        original_string = decrypt_string(api_key,
                                         key=b'YAboQcXx376HSUKqzkTz8LK1GKs19Skg4JoZH4QUCJc=')

        if not original_string:
            return None, None

        split_strings = original_string.split(' ')

        if len(split_strings) < 2:
            return None, None

        api_key = split_strings[0]
        angent_type = split_strings[1]

        if not api_key or not angent_type:
            return None, None

        return api_key, angent_type

    except Exception as e:
        logging.error(f"Error occurred while validating API key: {e}")
        return None, None


# 验证给定的 OpenAI API 密钥是否可以正常访问。
def validate_api_key(api_key: str) -> bool:
    """
    验证给定的 OpenAI API 密钥是否可以正常访问。
    :param api_key: 加密的 API 密钥字符串
    :return: 如果 API 密钥有效且可访问，返回 True；否则返回 False
    """
    # 提取有效的 API 密钥和类型
    api_key_value, agent_type = get_key_info(api_key)

    if not api_key_value:
        logging.info(f"API KEY not found in the DB.")
        return False  # 提取失败，返回 False

    # 加载环境变量
    dotenv_path = find_env_file()  # 调用函数
    load_dotenv(dotenv_path)  # 加载环境变量
    base_url = os.getenv('BASE_URL')

    if not base_url:
        logging.error(f"BASE_URL not found in the environment variables.")
        return False

    # 创建 OpenAI 客户端
    client = OpenAI(api_key=api_key_value, base_url=base_url)
    try:
        # 尝试调用 OpenAI API 来验证 API 密钥，设置超时
        client.models.list(timeout=5)  # 5秒超时
        return True  # 如果成功，返回 True
    except OpenAIError as e:
        logging.error(f"PI error: {e}")
        return False  # 如果发生错误，返回 False


if __name__ == '__main__':
    api_key, angent_type = get_key_info(
        api_key='gAAAAABm3caZ_G7CB7dY68lUZFKALNDo2CTyYFyPmNsBxnqfJXuSxiLzz4NIp9cJBr6eHr__uOUKo-TPjyM8M2ileLkY-HaBLksBFzYERNv-7C58DZQUZoDgD8AWNOq83qzXMCkK54j2L3EMZb_4Wr7HyH_Q3dtMT0mvMwRfVB-FdePKcnQbgENC_QjQ1pqruLVbPhK1PlfKHcN_JtKtJzHA0Y-6iuAEtGw2meRau8lMebvJCOo8JcjIISILyjtVeM5TjVdqrwjehdLJt5eZznVuqRdO6v20fDE6kfUlPlGGZpjcPr2NQSE=')

    ans = validate_api_key(
        api_key='gAAAAABm3caZ_G7CB7dY68lUZFKALNDo2CTyYFyPmNsBxnqfJXuSxiLzz4NIp9cJBr6eHr__uOUKo-TPjyM8M2ileLkY-HaBLksBFzYERNv-7C58DZQUZoDgD8AWNOq83qzXMCkK54j2L3EMZb_4Wr7HyH_Q3dtMT0mvMwRfVB-FdePKcnQbgENC_QjQ1pqruLVbPhK1PlfKHcN_JtKtJzHA0Y-6iuAEtGw2meRau8lMebvJCOo8JcjIISILyjtVeM5TjVdqrwjehdLJt5eZznVuqRdO6v20fDE6kfUlPlGGZpjcPr2NQSE=')
    print(ans)
