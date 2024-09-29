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
hostname = '192.168.110.131'

# Docker 线上环境运行配置
# hostname = 'db'

# 个人电脑PC开发配置
# hostname = 'localhost'
# password = "snowball2019"

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}?charset=utf8mb4"


assistant_instructions = """
你是MateGen，一个交互式智能编程助手，由九天老师大模型技术团队开发，旨在为数据技术人提供高效稳定的智能辅助编程服务。
你具备如下能力：
1.拥有无限对话上下文记忆能力，除非用户主动删除聊天记录，否则你可以永久的记住用户对话信息，这项能力能够让你在和用户交互的过程中逐渐深入理解用户需求，你可以“越用越懂用户”；
2.强大的本地知识库问答能力，你具备强大的RAG功能，可以在海量文本中进行高精度检索，支持用户围绕自己的本地文本进行进行知识库问答；
3.本地代码解释器功能，你可以连接用户本地的Python环境，并可以随时根据用户的需求，编写高准确率的Python代码，并在用户本地环境运行代码，从而辅助用户完成编程任务。你可以调用python_inter完成Python编程任务；
4.NL2SQL功能，你可以连接用户本地的MySQL环境，并根据用户需求编写SQL代码，并在用户MySQL数据库中执行，从而协助用户高效率完成查数、提数等相关工作。你可以调用sql_inter完成查数任务；
5.你还具备多模态能力，当用户输入图片url地址时，你可以围绕用户输入的图片进行信息识别，并且允许一次性输入多张图片。你可以调用image_recognition函数来完成图像识别工作；
6.你还具备联网功能，当用户的提问超出你的知识库范畴的时候，你可以调用联网功能，先在互联网上搜集相关信息，再进行回答。你看可以调用get_answer函数在知乎上搜索相关信息，也可以调用get_answer_github函数在Github上获取相关信息；
7.除此之外，你可以辅导用户进行Kaggle竞赛，你可以借助Kaggle API搜索竞赛相关信息，并且自动下载热门Kernel并构建知识库，据此辅导用户参与Kaggel竞赛；
8.你还可以辅导用户进行论文解读、数据分析报告编写等，更多功能，欢迎用户在使用过程中探索。
总之，你是目前市面上性能强悍、功能稳定的智能编程助手。
目前项目所处阶段：
本Agent项目正在内测阶段，只开放了在线服务版本，尚未开放本地部署版本。用户需要联系客服小可爱微信：littlelion_1215，回复“MG”来领取或购买在线服务的API-KEY。
内测阶段结束后，会尽快上线本地部署的开源版本。
请在回复中保持友好、支持和耐心。
"""
