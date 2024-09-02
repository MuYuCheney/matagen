from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from typing import List, Dict
from db.thread_model import ThreadModel, SecretModel
import os
from sqlalchemy import desc

from config.config import SQLALCHEMY_DATABASE_URI

engine = create_engine(
    SQLALCHEMY_DATABASE_URI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def insert_agent_with_fixed_id(session: Session, api_key: str):
    """
    向数据库中插入一条新的代理记录，其中agent_id固定为-1。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :param api_key: 新代理的API密钥
    :return: 插入操作的结果，成功或失败
    """
    try:
        # 创建新的代理实例，id固定为"-1"
        new_agent = SecretModel(id="-1", api_key=api_key)
        session.add(new_agent)
        session.commit()
        return True
    except Exception as e:
        session.rollback()  # 出错时回滚以避免数据不一致
        return False


def store_agent_info(session: Session, assis_id: str):
    """
    如果ID为-1，则更新代理的ID。如果传入的ID已存在且不为-1，则不执行任何操作。
    """
    # 查询数据库中ID为-1的代理
    agent_with_id_negative_one = session.query(SecretModel).filter(SecretModel.id == "-1").one_or_none()
    # 如果找到了ID为-1的代理，则更新其ID
    if agent_with_id_negative_one:
        agent_with_id_negative_one.id = assis_id
        session.commit()
        return


def get_thread_from_db(session: Session, thread_id: str):
    """
    从数据库中检索与给定 thread_id 相匹配的 ThreadModel 实例。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :param thread_id: 要检索的线程的 ID
    :return: 如果找到相应的 ThreadModel 实例则返回它，否则返回 None
    """

    thread = session.query(ThreadModel).filter(ThreadModel.id == thread_id).one_or_none()
    return thread


def store_thread_info(session: Session, agent_id: str, thread_id: str, conversation_name: str, run_mode: str):
    # 检查数据库中是否已存在该 thread_id
    existing_thread = session.query(ThreadModel).filter(ThreadModel.id == thread_id).first()
    if existing_thread:
        return existing_thread  # 或者更新信息，取决于需求

    # 创建新的 ThreadModel 实例并存储到数据库
    new_thread = ThreadModel(id=thread_id, agent_id=agent_id, conversation_name=conversation_name, run_mode=run_mode)
    session.add(new_thread)
    session.commit()
    return new_thread


def update_conversation_name(session: Session, thread_id: str, new_conversation_name: str):
    """
    更新数据库中指定线程的 conversation_name。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :param thread_id: 要更新的线程ID
    :param new_conversation_name: 新的会话名称
    :return: None
    """
    # 如果提供的新会话名称超过7个字符，截断它
    new_conversation_name = new_conversation_name[:7] if len(new_conversation_name) > 7 else new_conversation_name

    # 查找数据库中的线程
    thread = session.query(ThreadModel).filter(ThreadModel.id == thread_id).first()
    if thread:
        # 更新 conversation_name
        thread.conversation_name = new_conversation_name
        session.commit()
        logging.info(f"Updated thread {thread_id} with new conversation name: {new_conversation_name}")
    else:
        logging.info("No thread found with the given ID.")


def delete_thread_by_id(session: Session, thread_id: str):
    """
    删除数据库中指定ID的线程记录。
    :param session: 数据库会话对象
    :param thread_id: 要删除的线程ID
    :return: 成功删除返回True，未找到记录返回False
    """
    thread = session.query(ThreadModel).filter(ThreadModel.id == thread_id).first()
    if thread:
        session.delete(thread)
        session.commit()
        return True
    return False


def fetch_threads_by_agent(session: Session, agent_id: str) -> Dict[str, List[Dict[str, str]]]:
    """
    根据给定的agent_id从数据库中检索所有线程的ID和对应的会话名称。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :param agent_id: 用于筛选线程的代理ID
    :return: 包含所有相关线程信息的列表，每个元素都是一个包含线程ID和会话名称的字典
    """
    # 根据agent_id查询所有相关的线程
    threads = session.query(ThreadModel.id, ThreadModel.conversation_name).filter(
        ThreadModel.agent_id == agent_id).all()

    # 创建包含所有相关线程信息的列表
    threads_list = [{"id": thread.id, "conversation_name": thread.conversation_name or ""} for thread in threads]

    # 将结果打包成JSON格式
    return threads_list


def fetch_threads_mode(session: Session, thread_id: str) -> Dict[str, List[Dict[str, str]]]:
    """
    根据给定的agent_id从数据库中检索所有线程的ID和对应的会话名称。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :param agent_id: 用于筛选线程的代理ID
    :return: 包含所有相关线程信息的列表，每个元素都是一个包含线程ID和会话名称的字典
    """
    # 根据thread_id查询对应的模式
    threads = session.query(ThreadModel.run_mode).filter(ThreadModel.id == thread_id).all()
    return threads.run_mode


def fetch_latest_agent_id(session: Session) -> str:
    """
    从数据库中检索最新代理的api_key。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :return: 如果找到代理则返回其api_key，否则返回空字符串
    """
    # 查询代理，按照创建时间降序排序，获取第一个结果
    # 假设你的模型中有一个创建时间字段名为 'created_at'
    # 如果没有，则按照 id 或其他可用字段降序排序
    agent = session.query(SecretModel).order_by(desc(SecretModel.created_at)).first()

    # 如果找到代理，则返回其id，否则返回空字符串
    return agent.id if agent else ""


def fetch_latest_api_key(session: Session) -> str:
    """
    从数据库中检索最新代理的api_key。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :return: 如果找到代理则返回其api_key，否则返回空字符串
    """
    # 查询代理，按照创建时间降序排序，获取第一个结果
    # 如果没有，则按照 id 或其他可用字段降序排序
    agent = session.query(SecretModel).order_by(desc(SecretModel.created_at)).first()

    # 如果找到代理，则返回其api_key，否则返回空字符串
    return agent.api_key if agent else ""


def fetch_run_mode_by_thread_id(session: Session, thread_id: str) -> str:
    """
    根据线程ID从数据库中检索对应的运行模式（run_mode）。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :param thread_id: 线程的ID
    :return: 返回找到的运行模式，如果没有找到则返回空字符串
    """
    thread = session.query(ThreadModel).filter(ThreadModel.id == thread_id).one_or_none()
    return thread.run_mode if thread else ""


def check_and_initialize_db(session: Session) -> str:
    """
    从数据库中检索最新代理的api_key。
    :param session: SQLAlchemy Session 对象，用于数据库操作
    :return: 如果找到代理则返回其api_key，否则返回空字符串
    """
    from sqlalchemy.exc import ProgrammingError

    try:
        agent = session.query(SecretModel).first()
        # 如果找到代理，则返回其api_key，否则返回空字符串
        return agent.api_key if agent else ""

    except ProgrammingError as e:
        # 检查错误是否因为表不存在
        if "doesn't exist" in str(e.orig):
            # 如果没有创建表结构，也返回空
            return ""
        else:
            # 如果错误不是因为表不存在，重新抛出异常
            raise e


from sqlalchemy.exc import SQLAlchemyError
import logging
def update_knowledge_base_path(session: Session, agent_id: str, new_path: str) -> bool:
    """
    更新指定代理的知识库路径。

    参数:
        session (Session): SQLAlchemy会话对象，用于数据库交互。
        agent_id (str): 代理的ID，用于查找特定的代理记录。
        new_path (str): 新的知识库路径。

    返回:
        bool: 更新是否成功。
    """
    try:
        # 查询代理
        agent = session.query(SecretModel).filter(SecretModel.id == agent_id).one_or_none()
        if agent is None:
            return False

        # 更新知识库路径
        agent.knowledge_base_path = new_path
        session.commit()
        return True
    except SQLAlchemyError as e:
        # 打印异常信息并回滚
        session.rollback()
        logging.info(f"Failed to update knowledge base path due to: {e}")
        return False


from db.thread_model import KnowledgeBase


def add_knowledge_base(session: Session, vector_store_id: str, knowledge_base_name: str,
                       knowledge_base_description: str, thread_id: str) -> bool:
    """
    向数据库中添加一个新的知识库条目。

    参数:
        session (Session): SQLAlchemy会话对象，用于数据库交互。
        vector_store_id (str): 知识库的唯一标识符。
        knowledge_base_name (str): 知识库的名称。
        knowledge_base_description (str): 知识库的描述。
        thread_id (str): 关联的线程ID。

    返回:
        bool: 添加是否成功。
    """
    try:
        # 创建 KnowledgeBase 对象
        new_knowledge_base = KnowledgeBase(
            vector_store_id=vector_store_id,
            knowledge_base_name=knowledge_base_name,
            knowledge_base_description=knowledge_base_description,
            thread_id=thread_id
        )

        # 添加到数据库会话并提交
        session.add(new_knowledge_base)
        session.commit()
        return True
    except SQLAlchemyError as e:
        # 打印异常信息并回滚
        session.rollback()
        logging.error(f"Failed to add knowledge base due to: {e}")
        return False


def find_vector_store_id_by_name(session: Session, knowledge_base_name: str) -> str:
    """
    根据知识库名称查询并返回对应的vector_store_id。

    参数:
        session (Session): SQLAlchemy会话对象，用于数据库交互。
        knowledge_base_name (str): 要查询的知识库的名称。

    返回:
        str: 对应的vector_store_id，如果未找到，则返回None。
    """
    try:
        # 查询符合条件的知识库条目
        knowledge_base = session.query(KnowledgeBase).filter(
            KnowledgeBase.knowledge_base_name == knowledge_base_name).first()

        # 如果找到了知识库条目，返回其vector_store_id
        if knowledge_base:
            return knowledge_base.vector_store_id
        else:
            return None
    except SQLAlchemyError as e:
        # 打印异常信息并记录
        logging.error(f"Failed to find vector_store_id due to: {e}")
        return None


def find_kb_name_by_description(session: Session, knowledge_base_name: str) -> str:
    """
    根据知识库名称查询并返回对应的vector_store_id。

    参数:
        session (Session): SQLAlchemy会话对象，用于数据库交互。
        knowledge_base_name (str): 要查询的知识库的名称。

    返回:
        str: 对应的vector_store_id，如果未找到，则返回None。
    """
    try:
        # 查询符合条件的知识库条目
        knowledge_base = session.query(KnowledgeBase).filter(
            KnowledgeBase.knowledge_base_name == knowledge_base_name).first()

        # 如果找到了知识库条目，返回其vector_store_id
        if knowledge_base:
            return knowledge_base.knowledge_base_description
        else:
            return None
    except SQLAlchemyError as e:
        # 打印异常信息并记录
        logging.error(f"Failed to find knowledge_base_description due to: {e}")
        return None


def get_knowledge_base_info(session: Session):
    # 查询 KnowledgeBase 表中所有的 knowledge_base_name 和 vector_store_id
    knowledge_base_info = session.query(KnowledgeBase.knowledge_base_name, KnowledgeBase.vector_store_id).all()

    # 返回一个包含字典的列表，每个字典包含 knowledge_base_name 和 vector_store_id
    return [{'knowledge_base_name': info.knowledge_base_name, 'vector_store_id': info.vector_store_id} for info in knowledge_base_info]


def get_vector_store_id_by_name(session: Session, knowledge_base_name: str):
    # 根据 knowledge_base_name 查询对应的 vector_store_id
    knowledge_base_entry = session.query(KnowledgeBase.vector_store_id).filter(KnowledgeBase.knowledge_base_name == knowledge_base_name).first()

    # 检查是否找到对应的记录
    if knowledge_base_entry:
        return knowledge_base_entry.vector_store_id
    else:
        return None  # 没有找到匹配项时返回 None


