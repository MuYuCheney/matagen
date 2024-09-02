from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from sqlalchemy import create_engine

# 用于创建一个基类，该基类将为后续定义的所有模型类提供 SQLAlchemy ORM 功能的基础。
Base = declarative_base()


class SecretModel(Base):
    __tablename__ = 'agents'
    id = Column(String(255), primary_key=True)  # 考虑将 'id' 重命名为 'assis_id'，如果它直接存储 'assis_id'
    api_key = Column(String(768), unique=True, nullable=False)  # 确保 api_key 是唯一的
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 自动生成创建时间

    threads = relationship("ThreadModel", back_populates="agent", cascade="all, delete-orphan")


class ThreadModel(Base):
    __tablename__ = 'threads'
    id = Column(String(255), primary_key=True)  # 这作为 'thread_id'
    agent_id = Column(String(255), ForeignKey('agents.id'))
    conversation_name = Column(String(255))
    run_mode = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 自动生成创建时间

    # 添加与 KnowledgeBase 的反向关系
    knowledge_bases = relationship("KnowledgeBase", back_populates="thread")

    # 假设还有一个 SecretModel 类定义
    agent = relationship("SecretModel", back_populates="threads")

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_bases'

    # 主键字段
    vector_store_id = Column(String(255), primary_key=True)

    # 知识库的名称
    knowledge_base_name = Column(String(255), nullable=False)

    # 知识库描述
    knowledge_base_description = Column(Text, nullable=True)

    # 外键字段，链接到 threads 表的 id 字段
    thread_id = Column(String(255), ForeignKey('threads.id'))

    # 建立与 ThreadModel 的关系
    thread = relationship("ThreadModel", back_populates="knowledge_bases")


class DbBase(Base):
    __tablename__ = 'db_configs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hostname = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    database_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())  # 自动生成创建时间

# 定义数据库模型初始化函数
def initialize_database(username: str, password: str, hostname: str, database_name: str):
    try:
        database_url = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}?charset=utf8mb4"
        engine = create_engine(database_url, echo=True)

        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        from sqlalchemy.exc import SQLAlchemyError
        from sqlalchemy.inspection import inspect
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)

        session.execute(
            text("ALTER DATABASE {} CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci".format(database_name)))
        session.commit()

        inspector = inspect(engine)

        # 删除知识库表的外键
        if inspector.has_table("knowledge_bases", schema="mategen"):
            session.execute(text("ALTER TABLE knowledge_bases DROP FOREIGN KEY knowledge_bases_ibfk_1"))
            session.commit()

        # 删除线程表的外键
        if inspector.has_table("threads", schema="mategen"):
            session.execute(text("ALTER TABLE threads DROP FOREIGN KEY threads_ibfk_1"))
            session.commit()

        # 修改表字符集
        tables_to_modify = ['threads', 'agents', 'knowledge_bases', "db_configs"]
        for table_name in tables_to_modify:
            if inspector.has_table(table_name, schema="mategen"):
                session.execute(
                    text(f"ALTER TABLE {table_name} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                session.commit()

        # 重新添加外键
        if inspector.has_table("threads", schema="mategen"):
            session.execute(text(
                "ALTER TABLE threads ADD CONSTRAINT threads_ibfk_1 FOREIGN KEY (agent_id) REFERENCES agents(id)"))
            session.commit()

        # 重新添加知识库表的外键
        if inspector.has_table("knowledge_bases", schema="mategen"):
            session.execute(text(
                "ALTER TABLE knowledge_bases ADD CONSTRAINT knowledge_bases_ibfk_1 FOREIGN KEY (thread_id) REFERENCES threads(id)"))
            session.commit()

        return True
    except Exception as e:
        print("Error occurred during database initialization:", e)
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == '__main__':
    # 开发环境
    from config.config import SQLALCHEMY_DATABASE_URI

    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    Base.metadata.create_all(engine)
