#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, HTTPException, Depends, Body, status, Security
from fastapi.responses import JSONResponse
import uvicorn
import json
import argparse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel
from fastapi import Depends, Query
from fastapi.security import APIKeyHeader
from openai import OpenAI

from MateGen.mateGenClass import (MateGenClass,
                                  get_vector_db_id,
                                  create_knowledge_base,
                                  create_knowledge_base_folder,
                                  print_and_select_knowledge_base,
                                  update_knowledge_base_description,
                                  delete_all_files,
                                  get_latest_thread,
                                  make_hl,
                                  )
from init_interface import get_mate_gen, get_openai_instance
from func_router import get_knowledge_bases
from pytanic_router import KbNameRequest

# 全局变量来存储MateGenClass实例
global_instance = None
global_openai_instance = None


class ChatRequest(BaseModel):
    question: str = Body("", embed=True)
    chat_stream: bool = Body(False, embed=True)


class UrlModel(BaseModel):
    url: str


class KnowledgeBaseCreateRequest(BaseModel):
    knowledge_base_name: str = Body(..., embed=True, description="知识库的名称")
    chunking_strategy: str = Body("auto", embed=True, description="参数类型，自动参数为auto，手动参数为 static")
    max_chunk_size_tokens: int = Body(800, embed=True)
    chunk_overlap_tokens: int = Body(400, embed=True)
    folder_path_base: str = Body(None, embed=True, description="可忽略")  # 可选字段


class KnowledgeBaseDescriptionUpdateRequest(BaseModel):
    sub_folder_name: str
    description: str


class CodeExecutionRequest(BaseModel):
    python_code: str
    thread_id: str


class SQLExecutionRequest(BaseModel):
    thread_id: str
    db_info_id: str
    sql_query: str


def create_app():
    app = FastAPI(
        title="MateGen API Server",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载路由
    mount_app_routes(app)

    # 挂载 前端 项目构建的前端静态文件夹 (对接前端静态文件的入口)
    # Windows
    app.mount("/", StaticFiles(directory="../static/dist"), name="static")

    # # Docker
    # app.mount("/", StaticFiles(directory="/app/static/dist"), name="static")

    return app


import os

# 获取当前文件所在目录的上一级目录
# 获取当前文件所在目录的上一级目录
current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, '..', 'uploads')

# 创建上传文件夹（如果不存在）
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
from fastapi import FastAPI, File, UploadFile, Form
from typing import List

import shutil


def mount_app_routes(app: FastAPI):
    """
    这里定义所有 RestFul API interfence
    待做：
    1. 获取用户全部的历史对话会话框
    2. 获取某个会话框内的全部对话内容
    3.
    """

    @app.get("/api/check_initialization", tags=["Initialization"],
             summary="检查当前用户是否第一次启动项目，如果是，跳转到API_Key弹窗页面，调用/api/set_api_key")
    def check_database_initialization():
        """
        检查数据库是否已初始化并根据需要进行初始化。
        """
        from MateGen.utils import SessionLocal, check_and_initialize_db

        db_session = SessionLocal()

        # 如果数据表结构不为空，则直接进入对话模型，不需要进行初始化
        if check_and_initialize_db(db_session) == '':
            return {"status": 500,
                    "data": {"message": "当前用户初次启动项目，请跳转项目初始化页面，引导用户完成项目初始化工作"}}

        return {"status": 200, "data": {"message": "项目已完成过初始化配置，可直接进行对话"}}

    # 初始化API，单独做以解决 API_KEY 加密问题
    @app.post("/api/set_api_key", tags=["Initialization"], summary="授权有效的API Key，需要让用户手动填入")
    def save_api_key(api_key: str = Body(..., description="用于问答的密钥", embed=True),
                     ):
        from MateGen.utils import SessionLocal, insert_agent_with_fixed_id
        db_session = SessionLocal()
        try:
            from init_interface import get_key_valid
            if get_key_valid(api_key):
                # 存储用户加密后的 API_KEY, Assis ID 设置为-1来标识，否则会被替换成解密后的API Key
                insert_agent_with_fixed_id(db_session, api_key)
                return {"status": 200, "data": {"message": "您输入的 API Key 已生效。"}}
            else:
                return {"status": 500, "data": {"message": "您输入的 API Key 无效或已过期。"}}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # 初始化MetaGen实例，保存在全局变量中，用于后续的子方法调用
    @app.post("/api/initialize", tags=["Initialization"],
              summary="默认空参，是新建对话功能。\n"
                      "在当前会话页面下： \n"
                      "1. 如果选择了知识库，重新调用该方法，传递参数为：thread_id, knowledge_base_chat：true，knowledge_base_name_id：xxx \n"
                      "2. 如果选择了数据库，重新调用该方法，传递参数是：thread_id, db_name_id：xxx \n"
                      "3. 如果知识库和数据库都选择了，重新调用该方法，同时传递上述四个参数: "
                      "thread_id, knowledge_base_chat：true, knowledge_base_name_id, db_name_id \n")
    def initialize_mate_gen(mate_gen: MateGenClass = Depends(get_mate_gen),
                            openai_ins: OpenAI = Depends(get_openai_instance),
                            thread: str = Body(None, description="会话id")):
        try:
            global global_instance, global_openai_instance
            global_instance = mate_gen
            global_openai_instance = openai_ins

            # 这里根据初始化结果返回相应的信息
            return {"status": 200, "data": {"message": "MateGen 实例初始化成功",
                                            "thread_id": global_instance.thread_id}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/upload", tags=["Knowledge"], summary="上传文件功能。\n"
                                                         "进行知识库解析操作前,先调用此函数，确保文件全部上传后，再进行/api/create_knowledge")
    async def upload_files(
            folderName: str = Form(...),  # 接收文件夹名称
            files: List[UploadFile] = File(...)  # 接收多个文件
    ):
        uploaded_files = []

        try:
            # 生成指定文件夹路径
            folder_path = os.path.join(UPLOAD_FOLDER, folderName)
            os.makedirs(folder_path, exist_ok=True)

            for file in files:
                # 文件存储路径
                file_location = os.path.join(folder_path, file.filename)

                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                uploaded_files.append(file.filename)
            return {"status": 200, "data": {"message": "所有文件上传服务器成功",
                                            "files": uploaded_files,
                                            "folder": folderName}}

        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=500)

    @app.post("/api/create_knowledge", tags=["Knowledge"],
              summary="知识库解析")
    def create_knowledge(request: KnowledgeBaseCreateRequest, thread_id: str = Query(...,
                                                                                     description="传递当前会话状态下的thread_id")):
        # 这里要根据chunking_strategy策略设定RAG的切分策略，默认是自动
        vector_id = create_knowledge_base(client=global_openai_instance,
                                          knowledge_base_name=request.knowledge_base_name,
                                          chunking_strategy=request.chunking_strategy,
                                          max_chunk_size_tokens=request.max_chunk_size_tokens,
                                          chunk_overlap_tokens=request.chunk_overlap_tokens,
                                          thread_id=thread_id)
        if vector_id is not None:
            return {"status": 200, "data": {"message": "已成功完成知识库创建",
                                            "vector_id": vector_id}}
        else:
            raise HTTPException(status_code=400, detail="知识库无法创建，请确认知识库文件夹中均为格式合规的文件，"
                                                        "目前仅支持 .md, .pdf, .doc, .docx, .ppt, .pptx 文件类型")

    @app.get("/api/get_all_knowledge", tags=["Knowledge"],
             summary="获取所有已解析成功的知识库名称列表")
    def get_all_knowledge():
        from MateGen.utils import SessionLocal, get_knowledge_base_info
        db_session = SessionLocal()
        try:
            knowledge_bases = get_knowledge_base_info(db_session)
            if knowledge_bases == []:
                return {"status": 404, "data": [], "message": "没有找到知识库，请先进行创建"}
            return {"status": 200, "data": knowledge_bases}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/all_knowledge_base", tags=["Knowledge"],
             summary="根据知识库ID获取到其内部所有的归属文件")
    def get_knowledge_detail(knowledge_id: str = Query(..., description="知识库的id")):
        from MateGen.utils import SessionLocal, get_knowledge_base_name_by_id
        db_session = SessionLocal()
        try:
            knowledge_bases = get_knowledge_base_name_by_id(db_session, knowledge_id)
            return {"status": 200, "data": knowledge_bases}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/update_knowledge_base", tags=["Knowledge"],
              summary="目前先仅允许更改知识库名称，需要设置 init参数为false")
    def update_knowledge_info(knowledge_new_name: str = Body(..., description="thread_id"),
                              init: bool = Body(...,
                                                description="init=False，仅更改知识库名称"),
                              knowledge_id: str = Query(..., description="知识库id")):
        from MateGen.utils import SessionLocal, update_knowledge_base_name
        db_session = SessionLocal()
        try:
            if update_knowledge_base_name(db_session, knowledge_id, knowledge_new_name, init):
                return {"status": 200, "data": {"后台知识库已更新"}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/delete_knowledge/{knowledge_id}", tags=["Knowledge"], summary="根据知识库ID，删除指定知识库")
    def api_delete_all_files(knowledge_id: str):
        from MateGen.utils import SessionLocal, delete_knowledge_base_by_id
        db_session = SessionLocal()
        try:
            vector_store_id = delete_knowledge_base_by_id(db_session, knowledge_id)
            if vector_store_id is not None:
                # 向服务器请求实际删除
                global_openai_instance.beta.vector_stores.delete(
                    vector_store_id=vector_store_id
                )
                return {"status": 200, "data": {"message": "知识库删除成功。"}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def event_generator(question, code_type, run_result):
        from MateGen.mateGenClass import EventHandler
        response = global_instance.chat(question, chat_stream=True)

        from MateGen.utils import SessionLocal
        from db.thread_model import MessageModel
        db_session = SessionLocal()

        # 用来保留完整的模型回答
        full_text = ''
        if code_type != None:
            # 创建格式化的消息字符串
            message = (
                f"基于历史的聊天信息，这是我调试好的{code_type} 执行代码/语句，如下所示：\n"
                f"{question}\n"
                "运行结果如下所示：\n"
                f"{run_result}\n\n"
                "现在我将全部内容发送给你，你收到后请仅仅回复：您的代码/语句和运行结果已成功记录在当前会话中."
            )

            response[1].beta.threads.messages.create(
                thread_id=response[2],
                role="user",
                content=message,
            )

            with response[1].beta.threads.runs.stream(
                    thread_id=response[2],
                    assistant_id=response[0],
                    event_handler=EventHandler(),
            ) as stream:
                for text in stream.text_deltas:
                    full_text += text
                    if not text:  # 如果text为空，结束生成器
                        break
                    yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"
                yield "event: end\n\n"

                new_message = MessageModel(
                    thread_id=response[2],
                    question=question,
                    response=full_text,
                    message_type=code_type,
                    run_result=run_result,
                )

                db_session.add(new_message)
                db_session.commit()  # 提交事务
                db_session.close()

        else:
            response[1].beta.threads.messages.create(
                thread_id=response[2],
                role="user",
                content=question,
            )
            with response[1].beta.threads.runs.stream(
                    thread_id=response[2],
                    assistant_id=response[0],
                    event_handler=EventHandler(),
            ) as stream:
                for text in stream.text_deltas:
                    full_text += text
                    if not text:  # 如果text为空，结束生成器
                        break
                    yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"
                yield "event: end\n\n"
                # 插入消息到数据库
                new_message = MessageModel(
                    thread_id=response[2],
                    question=question,
                    response=full_text,
                    message_type='chat',
                )
                db_session.add(new_message)
                db_session.commit()  # 提交事务
                db_session.close()

    @app.get("/api/chat", tags=["Chat"],
             summary="用户输入框问答通用对话接口, 参数chat_stream默认为True 为流式输出, 采用SSE传输 \n"
                     "1. 如果是Python编辑框点击发送，query参数为代码，code_type为Python，run_result为运行结果 \n"
                     "2. 如果是SQL编辑框点击发送，query参数为Sql语句，code_type为SQL，run_result为运行结果")
    async def chat(query: str = Query(..., description="用户会话框输入的问题"),
                   chat_stream: bool = Query(True, description="是否采用流式输出,默认流式，可不传此参数"),
                   code_type: str = Query(None, description="类型：Python或SQL"),
                   run_result: str = Query(None, description="Python或者SQL运行结果"), ):
        if query == "init":
            return {"status": 200, "data": {"message": "无操作"}}
        try:
            if chat_stream:
                from sse_starlette.sse import EventSourceResponse
                # 使用SSE 流式处理
                event_response = EventSourceResponse(event_generator(query, code_type, run_result))
                event_response.headers.update({"Content-Type": "text/event-stream;data:text/plain"})
                return event_response
            else:
                # get 方法 无法 进入此逻辑，先保留
                response = global_instance.chat(query, chat_stream)
                return {"status": 200, "data": {"message": response['data']}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/conversation", tags=["Chat"], summary="获取所有聊天会话窗口名称")
    def get_conversation():
        from MateGen.utils import SessionLocal
        from db.thread_model import ThreadModel
        db_session = SessionLocal()
        try:
            # 添加.filter(ThreadModel.conversation_name != "new_chat") 来过滤掉名为 "new_chat" 的对话
            results = db_session.query(ThreadModel.id, ThreadModel.conversation_name) \
                .filter(ThreadModel.conversation_name != "new_chat") \
                .order_by(ThreadModel.created_at.desc()).all()
            data = [{"id": result.id, "conversation_name": result.conversation_name} for result in results]
            return {"status": 200, "data": {"message": data}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db_session.close()

    @app.get("/api/messages", tags=["Chat"], summary="根据thread_id获取指定会话的所有历史会话消息列表")
    def get_messages(thread_id: str = Query(..., description="thread_id")):
        try:
            from db.thread_model import MessageModel
            from MateGen.utils import SessionLocal
            from db.thread_model import ThreadModel
            from sqlalchemy import desc

            db_session = SessionLocal()

            messages = db_session.query(MessageModel).filter(MessageModel.thread_id == thread_id).order_by(
                desc(MessageModel.created_at)).all()

            # 封装数据
            chat_records = []
            for msg in messages:
                if msg.message_type != 'chat':
                    # 对非 chat 类型消息进一步提取 run_result
                    chat_record = {
                        'user': msg.question,
                        'assistant': msg.response,
                        'chat_type': msg.message_type,
                        'run_result': msg.run_result  # 这里添加 run_result 字段
                    }
                else:
                    chat_record = {
                        'user': msg.question,
                        'assistant': msg.response,
                        'chat_type': msg.message_type
                    }
                chat_records.append(chat_record)

            return {"status": 200, "data": {"message": chat_records}}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/api/update_conversation_name", tags=["Chat"], summary="根据thread_id更新会话框的显示名称")
    def update_conversation_name(thread_id: str = Body(..., description="thread_id"),
                                 new_conversation_name: str = Body(..., description="新的会话框名称")):
        from MateGen.utils import SessionLocal, update_conversation_name

        db_session = SessionLocal()
        try:
            update_conversation_name(db_session, thread_id, new_conversation_name)
            return {"status": 200, "data": {"message": "已更新"}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db_session.close()

    @app.delete("/api/delete_conversation", tags=["Chat"], summary="根据thread_id删除指定的会话窗口")
    def delete_thread(thread_id: str = Body(..., description="需要删除的thread_id", embed=True)):
        """
        根据提供的thread_id删除数据库中的线程记录。
        """
        from MateGen.utils import SessionLocal, delete_thread_by_id

        db_session = SessionLocal()

        try:
            # 删除数据库信息
            delete_thread_id = delete_thread_by_id(db_session, thread_id)
            if delete_thread_id is not None:
                # 服务器端进行删除
                global_openai_instance.beta.threads.delete(delete_thread_id)
                return {"status": 200, "data": {"message": f"会话 {thread_id} 已被删除"}}
            else:
                raise HTTPException(status_code=404, detail="未找到指定的会话ID")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除会话ID发生错误: {str(e)}")
        finally:
            db_session.close()

    from db_interface import DBConfig, insert_db_config, update_db_config, get_all_databases, \
        delete_db_config

    @app.post("/api/create_db_connection", tags=["Database"],
              summary="创建数据库连接")
    def db_create(db_config: DBConfig = Body(...)):
        try:
            database_id = insert_db_config(db_config)
            return {"status": 200, "data": {"message": "数据库连接信息正常",
                                            "db_info_id": database_id}}
        except Exception as e:
            raise e

    @app.get("/api/show_all_databases", tags=["Database"], summary="获取所有数据库连接信息")
    def list_databases():
        try:
            databases = get_all_databases()
            return {"status": 200, "data": databases}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/api/update_db_connection/{db_info_id}", tags=["Database"], summary="更新数据库连接配置")
    def update_db_connection(db_info_id: str, db_config: DBConfig = Body(...)):
        try:
            updated = update_db_config(db_info_id, db_config)
            if updated:
                return {"status": 200, "data": {"message": "数据库连接信息已更新", "db_info_id": db_info_id}}
            else:
                raise HTTPException(status_code=404, detail="未找到指定的数据库配置")
        except HTTPException as http_ex:
            raise http_ex
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"更新失败: {str(ex)}")

    @app.get("/api/get_db_info", tags=["Database"], summary="获取数据库连接配置")
    def get_db_connection(db_info_id: str = Query(..., description="数据库配置的 ID", embed=True)):

        from db_interface import get_db_config_by_id
        try:
            db_config = get_db_config_by_id(db_info_id)
            if db_config:
                return {"status": 200, "data": {"db_info": db_config}}
            else:
                raise HTTPException(status_code=404, detail="未找到指定的数据库配置")
        except HTTPException as http_ex:
            raise http_ex
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"更新失败: {str(ex)}")

    @app.delete("/api/delete_db_connection/{db_info_id}", tags=["Database"], summary="删除数据库连接配置")
    def delete_db_connection(db_info_id: str):
        try:
            success = delete_db_config(db_info_id)
            if not success:
                raise HTTPException(status_code=404, detail="Database configuration not found")
            return {"status": 200, "data": {"message": "数据库配置信息已成功删除"}}
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    from python_interface import execute_python_code
    @app.post("/api/execute_code", tags=["Python Execution"],
              summary="从指定会话窗口跳转到Python环境并执行代码")
    def execute_code(request: CodeExecutionRequest = Body(...)):
        # 检查thread_id是否提供
        if not request.thread_id:
            raise HTTPException(status_code=400, detail="thread_id is required to execute the code.")

        try:
            result = execute_python_code(request.python_code)
            return {"status": 200, "data": {"thread_id": request.thread_id, "message": result}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while executing the code: {str(e)}")

    @app.post("/api/execute_sql", tags=["SQL Execution"], summary="执行SQL语句并返回最终的结果")
    def execute_sql(request: SQLExecutionRequest = Body(...)):

        if not request.thread_id:
            raise HTTPException(status_code=400, detail="thread_id is required to execute the code.")

        try:
            from MateGen.utils import SessionLocal
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from db.thread_model import DbBase
            from sqlalchemy.exc import OperationalError

            db_session = SessionLocal()
            db_info = db_session.query(DbBase).filter(DbBase.id == request.db_info_id).one_or_none()
            db_session.close()

            # 确保只执行SELECT查询
            if not request.sql_query.lower().startswith("select"):
                raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")

            LOCAL_SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_info.username}:{db_info.password}@{db_info.hostname}:{db_info.port}/{db_info.database_name}?charset=utf8mb4"

            # 创建数据库引擎
            local_engine = create_engine(LOCAL_SQLALCHEMY_DATABASE_URI)

            # 尝试连接并执行一个简单的查询来检查连接
            try:
                # 创建会话
                Local_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=local_engine)
                local_db_session = Local_SessionLocal()
                # 测试数据库连接
                connection_test = local_db_session.execute(text("SELECT 1"))
                connection_test.fetchone()  # 尝试获取查询结果
                local_db_session.close()  # 正常则关闭会话
            except OperationalError as e:
                raise HTTPException(status_code=500, detail=f"连接数据库失败，请检查数据库是否处于正常运行状态: {str(e)}")

            # 如果连接测试通过，继续执行原来的查询
            local_db_session = Local_SessionLocal()
            result = local_db_session.execute(text(request.sql_query))
            results = result.fetchall()
            local_db_session.close()  # 执行完查询后关闭会话

            # 转换结果为字典列表
            output = []
            column_names = [col[0] for col in result.keys()]
            header = " | ".join(column_names)
            output.append(header)  # 首先添加头部，即列名

            for row in results:
                row_str = " | ".join(str(value) for value in row)
                output.append(row_str)

            db_session.close()

            return {"results": output}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"无法查询到该数据库的连接信息: {str(e)}")


def run_api(host, port, **kwargs):
    from config.config import username, password, hostname, database_name
    from db.thread_model import initialize_database

    # # 删除所有表
    # Base.metadata.drop_all(engine)
    # # 初始化操作
    initialize_database(username=username,
                        password=password,
                        hostname=hostname,
                        database_name=database_name)
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(app,
                    host=host,
                    port=port,
                    ssl_keyfile=kwargs.get("ssl_keyfile"),
                    ssl_certfile=kwargs.get("ssl_certfile"),
                    )
    else:
        uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--ssl_keyfile", type=str)
    parser.add_argument("--ssl_certfile", type=str)
    # 初始化消息
    args = parser.parse_args()
    args_dict = vars(args)

    app = create_app()

    run_api(host=args.host,
            port=args.port,
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile,
            )

    # app = create_app()
    # run_api(host="localhost",
    #         port=9000,
    #         ssl_keyfile=None,
    #         ssl_certfile=None,
    #         )
