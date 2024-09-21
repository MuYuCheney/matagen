import logging
import sys
import os

# 获取项目的根目录路径
base_path = os.path.dirname(os.path.abspath(__file__))


def setup_logging():
    """
    格式化服务实时日志信息
    :return:
    """
    # 创建一个logger
    logger = logging.getLogger()

    # 设置日志级别为INFO
    logger.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 创建一个handler，用于写入日志文件
    log_file_path = os.path.join(base_path, 'mategen_runtime.log')
    file_handler = logging.FileHandler(log_file_path)  # 使用完整路径指定日志文件名
    file_handler.setFormatter(formatter)  # 设置日志格式

    # 创建一个handler，用于将日志输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


username = 'root'
database_name = 'mategen'
password = "snowball950123"

# 公司环境开发配置
# hostname = '192.168.110.131'

# Docker 线上环境运行配置
hostname = 'db'

# 个人电脑PC开发配置
# hostname = 'localhost'
# password = "snowball2019"

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}?charset=utf8mb4"



