import logging
import sys

def setup_logging():
    # 创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 设置日志级别为INFO

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 创建一个handler，用于写入日志文件
    file_handler = logging.FileHandler('runtime.log')  # 指定日志文件名
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
#
# # # # 开发模式
# hostname = '192.168.110.131'
# SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}?charset=utf8mb4"


# # Docker Compose 中定义的 MySQL 服务名称
hostname = 'db'  # Docker Compose 中定义的 MySQL 服务名称
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}?charset=utf8mb4"

# # PC
# hostname = 'localhost'
# password = "snowball2019"
# SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}?charset=utf8mb4"

