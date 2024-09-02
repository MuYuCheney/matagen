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
    knowledge_base_name: str
    chunking_strategy: str = "auto"
    max_chunk_size_tokens: int = 800
    chunk_overlap_tokens: int = 400
    folder_path_base: str = None  # 可选字段


class KnowledgeBaseDescriptionUpdateRequest(BaseModel):
    sub_folder_name: str
    description: str


class CodeExecutionRequest(BaseModel):
    python_code: str
    thread_id: str


class SQLExecutionRequest(BaseModel):
    sql_query: str
    thread_id: str


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

    # # 挂载 前端 项目构建的前端静态文件夹 (对接前端静态文件的入口)
    # app.mount("/", StaticFiles(directory="static/dist"), name="static")

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
             summary="检查当前用户是否第一次启动项目，如果是，跳转到项目初始化页面")
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

    @app.post("/api/set_default_mysql", tags=["Initialization"],
              summary="初始化数据库，项目启动时直接后台调用，参数即Swapper中的默认参数 ")
    def default_mysql(
            username: str = Body('root', embed=True),
            password: str = Body('snowball950123', embed=True),
            hostname: str = Body('db', embed=True),
            database_name: str = Body('mategen', embed=True)
    ):
        from db.thread_model import initialize_database
        # 尝试初始化数据库
        if initialize_database(username, password, hostname, database_name):
            return {"status": 200, "data": {"message": "数据库初始化成功"}}
        else:
            raise HTTPException(status_code=500, detail="数据库初始化失败")

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
              summary="(新建对话)  MateGen 实例初始化 ")
    def initialize_mate_gen(mate_gen: MateGenClass = Depends(get_mate_gen),
                            openai_ins: OpenAI = Depends(get_openai_instance)):
        try:
            global global_instance, global_openai_instance
            global_instance = mate_gen
            global_openai_instance = openai_ins
            # 这里根据初始化结果返回相应的信息
            return {"status": 200, "data": {"message": "MateGen 实例初始化成功"}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/knowledge_initialize", tags=["Initialization"],
              summary="用于开启知识库问答的 MateGen 实例初始化")
    def initialize_knowledge_mate_gen(
            knowledge_base_chat: bool = Body(..., description="Enable knowledge base chat"),
            knowledge_base_name: str = Body(..., description="Name of the knowledge base if chat is enabled"),
            openai_ins: OpenAI = Depends(get_openai_instance)
    ):

        global global_instance, global_openai_instance
        from MateGen.utils import SessionLocal, fetch_latest_api_key
        db_session = SessionLocal()

        try:
            api_key = fetch_latest_api_key(db_session)

            mate_gen = get_mate_gen(api_key, None, False, knowledge_base_chat, False, None, knowledge_base_name)

            global_instance = mate_gen
            global_openai_instance = openai_ins
            # 这里根据初始化结果返回相应的信息
            return {"status": 200, "data": {"message": "MateGen 实例初始化成功", "kb_info": knowledge_base_name}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db_session.close()

    # 定义知识库对话（即如果勾选了知识库对话按钮后，重新实例化 MateGen 实例）
    @app.get("/api/reinitialize", tags=["Initialization"],
             summary="重新实例化MateGen类 (基于特定线程ID)")
    def reinitialize_mate_gen(
            thread_id: str = Query(..., description="Thread ID required for reinitialization"),
    ):

        global global_instance, global_openai_instance

        from MateGen.utils import SessionLocal, fetch_latest_api_key, fetch_run_mode_by_thread_id
        db_session = SessionLocal()

        # 根据运行模式，找到是 普通对话还是 知识库对话
        # 普通对话直接返回线程ID，知识库对话需要额外返回默认的知识库
        run_mode = fetch_run_mode_by_thread_id(db_session, thread_id)
        try:
            api_key = fetch_latest_api_key(db_session)

            if run_mode == "normal":
                mate_gen_instance = MateGenClass(
                    thread=thread_id,
                    api_key=api_key
                )
                global_instance = mate_gen_instance
                return {"status": 200,
                        "data": {"message": "当前会话状态的 MateGen 实例重新初始化成功", "thread_id": thread_id}}
            else:

                from MateGen.utils import SessionLocal, get_knowledge_base_info
                db_session = SessionLocal()

                knowledge_bases = get_knowledge_base_info(db_session)[-1]["knowledge_base_name"]

                # 默认选择第一个知识库
                mate_gen_instance = MateGenClass(
                    thread=thread_id,
                    api_key=api_key,
                    knowledge_base_chat=True,
                    knowledge_base_name=knowledge_bases
                )

                global_instance = mate_gen_instance
                return {"status": 200,
                        "data": {"message": "当前会话状态的 MateGen 实例重新初始化成功", "thread_id": thread_id,
                                 "kb_info": {knowledge_bases}}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db_session.close()

    @app.post("/api/upload", tags=["Knowledge"], summary="上传文件,在进行知识库解析前,先调用此函数上传全部文件")
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
              summary="新建一个本地知识库，并执行向量化操作")
    def create_knowledge(request: KnowledgeBaseCreateRequest, thread_id: str = Query(..., description="thread_id")):
        # 这里要根据chunking_strategy策略设定RAG的切分策略，默认是自动
        vector_id = create_knowledge_base(client=global_openai_instance,
                                          knowledge_base_name=request.knowledge_base_name,
                                          chunking_strategy=request.chunking_strategy,
                                          max_chunk_size_tokens=request.max_chunk_size_tokens,
                                          chunk_overlap_tokens=request.chunk_overlap_tokens,
                                          thread_id=thread_id)
        if vector_id is not None:
            return {"status": 200, "data": {"message": "已成功完成",
                                            "vector_id": vector_id}}
        else:
            raise HTTPException(status_code=400, detail="知识库无法创建，请再次确认知识库文件夹中存在格式合规的文件")

    @app.get("/api/get_all_knowledge", tags=["Knowledge"],
             summary="获取所有的本地知识库列表")
    def get_all_knowledge():
        from MateGen.utils import SessionLocal, get_knowledge_base_info
        db_session = SessionLocal()
        try:
            knowledge_bases = get_knowledge_base_info(db_session)
            if knowledge_bases == []:
                return {"status": 404, "data": [], "message": "没有找到知识库，请先创建。"}
            return {"status": 200, "data": knowledge_bases}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/all_knowledge_base", tags=["Knowledge"], summary="根据向量数据库id获取到上传的所有本地文件")
    def get_knowledge_base_all(request: KbNameRequest):

        from MateGen.utils import SessionLocal, get_vector_store_id_by_name
        db_session = SessionLocal()

        vector_store_id = get_vector_store_id_by_name(db_session, request.knowledge_base_name)

        # 根据输入的 知识库名称，先获取到对应的 向量库id
        vector_store_files = global_openai_instance.beta.vector_stores.files.list(
            vector_store_id=vector_store_id
        )

        # 遍历列表，提取并格式化所需信息
        formatted_files = [
            {
                "id": file.id,
                "created_at": file.created_at,
                "vector_store_id": file.vector_store_id
            }
            for file in vector_store_files.data
        ]

        return {"status": 200, "data": formatted_files}

    @app.delete("/api/delete_all_files", tags=["Knowledge"], summary="删除所有文件(待进一步确认)")
    def api_delete_all_files():
        vector_stores = global_openai_instance.beta.vector_stores.list()
        # TODO
        # if delete_all_files(global_openai_instance):
        #     return {"message": "所有文件已被成功删除。"}
        # else:
        #     raise HTTPException(status_code=500, detail="无法删除文件，请检查日志了解更多信息。")

    async def event_generator(question):
        from MateGen.mateGenClass import EventHandler
        response = global_instance.chat(question, chat_stream=True)  # 这个调用需要适应异步

        with global_openai_instance.beta.threads.runs.stream(
                thread_id=response["data"][0],
                assistant_id=response["data"][1],
                event_handler=EventHandler()
        ) as stream:
            # stream.until_done()
            # print(stream.text_deltas)
            for text in stream.text_deltas:
                yield json.dumps(
                    {"text": text},
                    ensure_ascii=False)

    @app.post("/api/chat", tags=["Chat"],
              summary="问答的通用对话接口, 参数chat_stream默认为False,如果设置为True 为流式输出, 采用SSE传输", )
    async def chat(request: ChatRequest):
        try:
            if request.chat_stream:
                from sse_starlette.sse import EventSourceResponse
                # 使用SSE 流式处理
                return EventSourceResponse(event_generator(request.question))
            else:
                response = global_instance.chat(request.question, request.chat_stream)
                return {"status": 200, "data": {"message": response['data']}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/agent_id", tags=["Chat"], summary="获取系统唯一的Assis id")
    def get_conversation():
        from MateGen.utils import SessionLocal, fetch_latest_agent_id

        db_session = SessionLocal()
        try:
            data = fetch_latest_agent_id(db_session)
            return {"status": 200, "data": {"message": data}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/conversation", tags=["Chat"], summary="获取指定代理的所有历史对话窗口")
    def get_conversation(agent_id: str = Query(..., description="assis id")):
        from MateGen.utils import SessionLocal, fetch_threads_by_agent

        db_session = SessionLocal()
        try:
            data = fetch_threads_by_agent(db_session, agent_id)
            return {"status": 200, "data": {"message": data}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db_session.close()

    @app.get("/api/messages", tags=["Chat"], summary="根据thread_id获取指定的会话历史信息")
    def get_messages(thread_id: str = Query(..., description="thread_id")):

        try:
            thread_messages = global_openai_instance.beta.threads.messages.list(thread_id).data

            dialogues = []  # 用于存储当前线程的对话内容

            # 遍历消息，按 role 提取文本内容
            for message in reversed(thread_messages):  # 反转列表处理，直接在循环中反转
                content_value = next((cb.text.value for cb in message.content if cb.type == 'text'), None)
                if content_value:
                    if message.role == "assistant":
                        dialogue = {"assistant": content_value}
                    elif message.role == "user":
                        dialogue = {"user": content_value}

                    dialogues.append(dialogue)

            return {"status": 200, "data": {"message": dialogues}}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/api/update_conversation_name", tags=["Chat"], summary="根据thread_id更新会话框的名称")
    def update_conversation_name(thread_id: str = Body(..., description="thread_id"),
                                 new_conversation_name: str = Body(..., description="thread_id")):
        from MateGen.utils import SessionLocal, update_conversation_name

        db_session = SessionLocal()
        try:
            update_conversation_name(db_session, thread_id, new_conversation_name)
            return {"status": 200, "data": {"message": "已更新"}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db_session.close()

    @app.delete("/api/delete_thread", tags=["Chat"], summary="删除指定的会话窗口")
    def delete_thread(thread_id: str = Body(..., description="需要删除的线程ID", embed=True)):
        """
        根据提供的thread_id删除数据库中的线程记录。
        """
        from MateGen.utils import SessionLocal, delete_thread_by_id

        db_session = SessionLocal()

        print(f"thread_id: {thread_id}")
        try:
            success = delete_thread_by_id(db_session, thread_id)
            if success:
                return {"status": 200, "data": {"message": f"Thread {thread_id} 已被删除"}}
            else:
                raise HTTPException(status_code=404, detail="未找到指定的线程")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除线程时发生错误: {str(e)}")
        finally:
            db_session.close()

    from db_interface import test_database_connection, DBConfig, insert_db_config, update_db_config, get_all_databases, delete_db_config

    @app.post("/api/test_db_connection", tags=["Database"],
              summary="创建数据库连接，如果连接成功，返回对应数据库中的所有表名")
    def db_connection(db_config: DBConfig = Body(...)):
        try:
            table_name = test_database_connection(db_config)
            return {"status": 200, "data": {"table_name": table_name}}
        except HTTPException as http_ex:
        # 直接抛出捕获的 HTTPException，这将保持异常中定义的状态码和错误信息
            raise http_ex
        except Exception as ex:
            # 捕获未预料到的其他异常，并转化为 HTTPException
            raise HTTPException(status_code=500, detail=f"未知错误: {str(ex)}")

    @app.post("/api/create_db_connection", tags=["Database"],
              summary="创建数据库连接，后端将进行连接存储")
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

            db_session = SessionLocal()

            # 确保只执行SELECT查询
            if not request.sql_query.lower().startswith("select"):
                raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")

            result = db_session.execute(text(request.sql_query))
            results = result.fetchall()

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
            raise HTTPException(status_code=500, detail=f"An error occurred while executing SQL: {str(e)}")


def run_api(host, port, **kwargs):
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
