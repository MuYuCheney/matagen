from MateGen.mateGenClass import MateGenClass
from fastapi import Depends
from fastapi import Body, HTTPException

from MateGen.mateGenClass import MateGenClass
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from openai import OpenAI
from MateGen.mateGenClass import decrypt_string


def get_mate_gen(
        api_key: str = Body(None, description="API key required for operation"),
        thread_id: str = Body(None, description="conversation id"),
        enhanced_mode: bool = Body(False, description="Enable enhanced mode"),
        knowledge_base_chat: bool = Body(False, description="Enable knowledge base chat"),
        knowledge_base_name_id: str = Body(None, description="id of the knowledge_base_chat is enabled"),
        db_name_id: str = Body(None, description="Database name"),
) -> MateGenClass:
    """
    用于生成 MateGen Class 的实例
    :param api_key:
    :param enhanced_mode:
    :param knowledge_base_chat:
    :param kaggle_competition_guidance:
    :param competition_name:
    :param knowledge_base_name:
    :return:
    """

    # 从数据库中获取 API_KEY
    from MateGen.utils import SessionLocal, fetch_latest_api_key
    db_session = SessionLocal()
    if api_key is None:
        api_key = fetch_latest_api_key(db_session)

        if knowledge_base_chat and not knowledge_base_name_id:
            raise HTTPException(status_code=400,
                                detail="knowledge_base_name is required when knowledge_base_chat is enabled.")
        return MateGenClass(api_key=api_key,
                            thread_id=thread_id,
                            enhanced_mode=enhanced_mode,
                            knowledge_base_chat=knowledge_base_chat,
                            knowledge_base_name_id=knowledge_base_name_id,
                            db_name_id=db_name_id
                            )
    else:
        return MateGenClass(api_key, thread_id, enhanced_mode, knowledge_base_chat, knowledge_base_name_id, db_name_id)


def get_openai_instance(
) -> OpenAI:
    """
    用于生成原始的 OpenAI  实例
    :param api_key:
    :return:
    """

    # 从数据库中获取 API_KEY
    from MateGen.utils import SessionLocal, fetch_latest_api_key
    db_session = SessionLocal()

    api_key = fetch_latest_api_key(db_session)

    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = os.path.join(BASE_DIR, '.env')

        load_dotenv(dotenv_path)
        base_url = os.getenv('BASE_URL')
        if not base_url:
            raise ValueError("BASE_URL not found in the environment variables.")

        original_string = decrypt_string(api_key, key=b'YAboQcXx376HSUKqzkTz8LK1GKs19Skg4JoZH4QUCJc=')
        if not original_string:
            raise ValueError("Failed to decrypt API key.")

        split_strings = original_string.split(' ')
        if not split_strings or len(split_strings) == 0:
            raise ValueError("Decrypted API key is invalid or empty.")

        s1 = split_strings[0]
        if not s1:
            raise ValueError("API key is empty after decryption and splitting.")

        return OpenAI(api_key=s1, base_url=base_url)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


def initialize_mate_gen(mate_gen: MateGenClass = Depends(get_mate_gen),
                        openai_ins: OpenAI = Depends(get_openai_instance)):
    try:
        global global_instance, global_openai_instance
        global_instance = mate_gen
        global_openai_instance = openai_ins

        # 这里根据初始化结果返回相应的信息
        return {"status": 200, "data": "MateGen 实例初始化成功"}
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


def get_key_valid(api_key):
    try:
        original_string = decrypt_string(api_key, key=b'YAboQcXx376HSUKqzkTz8LK1GKs19Skg4JoZH4QUCJc=')
        if not original_string:
            return False

        split_strings = original_string.split(' ')
        if not split_strings or len(split_strings) == 0:
            return False

        s1 = split_strings[0]
        if not s1:
            return False

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = os.path.join(BASE_DIR, '.env')

        load_dotenv(dotenv_path)
        base_url = os.getenv('BASE_URL')
        if not base_url:
            raise ValueError("BASE_URL not found in the environment variables.")
        client = OpenAI(api_key=s1, base_url=base_url)

        try:
            client.beta.assistants.create(
                instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
                name="Math Tutor",
                tools=[{"type": "code_interpreter"}],
                model="gpt-4o",
            )
            return True
        except:
            return False

    except Exception:
        return False
