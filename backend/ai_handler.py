from fastapi import APIRouter, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
import pydantic
import bleach
from typing import AsyncGenerator
from ai_caller import agent_callers
from ai_procedure import get_next_question
from user_context_singleton import context_manager
from config import QUESTIONS
import re
import json
import time

ai_handler = APIRouter()

def input_cleaner(input_str: str) -> str:
    """
    清理输入字符串，防止潜在的脚本注入攻击。
    """
    cleaned_str = bleach.clean(input_str, tags=[], attributes={}, strip=True)
    return cleaned_str

@ai_handler.get("/test")
async def test():
    time.sleep(5)
    def gen():
        test_data = [
            "这是测试数据1",
            "这是一个较长的测试数据2，包含更多内容",
            "测试数据3 包含特殊字符 !@#$",
            "Test data 4 with English",
            "**数字测试 12345**",
            "测试数据6 换行测试\n新的一行",
            "测试数据7 with mixed 混合内容",
            "较短的测试8",
            "测试数据9 包含空格和标点符号，。！",
            "最后的测试数据10",
            "\n\n[点我看看](https://www.baidu.com)"
        ]
        for data in test_data:
            time.sleep(0.2) # 模拟AI的思考时间
            yield "data: {}\n\n".format(json.dumps({
                "content": data,
                "status": "answering"
            }, ensure_ascii=False))
    return StreamingResponse(gen(), media_type="text/event-stream")

@ai_handler.get('/test2')
async def test2():
    time.sleep(5)
    def gen():
        test_data = [
            "这是测试数据1",
            "这是一个较长的测试数据2，包含更多内容",
            "测试数据3 包含特殊字符 !@#$",
            "Test data 4 with English",
            "**数字测试 12345**",
            "测试数据6 换行测试\n新的一行",
            "测试数据7 with mixed 混合内容",
            "较短的测试8",
            "测试数据9 包含空格和标点符号，。！",
            "最后的测试数据10",
            "\n\n[点我看看](https://www.baidu.com)"
        ]
        all_data = ""
        
        for data in test_data:
            all_data += "data: {}\n\n".format(json.dumps({
                "content": data,
                "status": "answering"
            }, ensure_ascii=False))
        
        yield all_data
    return StreamingResponse(gen(), media_type="text/event-stream")

@ai_handler.get("/start/{uid}")
async def get_started(
    uid: str,
    tone: str = Query("neutral", description="The desired tone for the AI response (e.g., professional, friendly)"),
    bg_tasks: BackgroundTasks = BackgroundTasks(),
):
    context_manager.init_new_user(uid)
    chunks = []

    async def agent_event_stream(method:str, prompt:str, tone:str) -> AsyncGenerator[str, None]:
        try:
            for content_chunk in agent_callers(method=method, prompt=prompt, tone=tone):
                chunks.append(content_chunk)
                t = f"data: {json.dumps({'content': f'{content_chunk}', 'status': 'answering'}, ensure_ascii=False)}\n\n"
                # print(t)
                yield t # SSE 格式
        except ValueError as e: # 捕获 agent_callers_generator 可能抛出的 ValueError
            yield f"data: ERROR: {str(e)}\n\n"
        except Exception as e:
            # 记录更严重的错误
            print(f"Unhandled exception in stream: {e}")
            yield f"data: ERROR: An unexpected error occurred.\n\n"
        finally:
            yield f'data: {{"content": "", "status": "ended"}}\n\n'
            # 将chunks列表中的内容合并为字符串，并提取被**包裹的内容
        pattern = r'\*\*(.*?)\*\*'
        try:
            plain_question = re.findall(pattern, "".join(chunks))[-1]
        except:
            print("".join(chunks))
            plain_question = "".join(chunks)
        bg_tasks.add_task(context_manager.start_new_question, uid, plain_question, 'given')

    return StreamingResponse(agent_event_stream(method='first_hello', prompt=QUESTIONS[0], tone=tone), media_type="text/event-stream")
      
class AnswerRequest(pydantic.BaseModel):
    uid: str
    answer: str

@ai_handler.post("/answer")
async def answer_question(
    request: AnswerRequest,
    bg_tasks: BackgroundTasks = BackgroundTasks(),
):
    cleaned_answer = input_cleaner(request.answer)
    updated = context_manager.update_answer(request.uid, cleaned_answer)
    if updated:
        return {"status": "success"}
    else:
        return {"status": "error"}

@ai_handler.get("/next-question/{uid}")
async def stream_ai_response(
    uid: str,
    tone: str = Query("neutral", description="The desired tone for the AI response (e.g., professional, friendly)"),
    bg_tasks: BackgroundTasks = BackgroundTasks()
) -> StreamingResponse:

    async def agent_event_stream(method:str, prompt:str, tone:str) -> AsyncGenerator[str, None]:
        try:
            for content_chunk in get_next_question(uid=uid, tone=tone):
                yield f"data: {json.dumps({'content': f'{content_chunk}', 'status': 'answering'}, ensure_ascii=False)}\n\n" # SSE 格式
                # await asyncio.sleep(0.01) # 如果需要，可以稍微延迟以模拟真实流
        except ValueError as e: # 捕获 agent_callers_generator 可能抛出的 ValueError
            yield f"data: ERROR: {str(e)}\n\n"
        except Exception as e:
            # 记录更严重的错误
            print(f"Unhandled exception in stream: {e}")
            yield f"data: ERROR: An unexpected error occurred.\n\n"
        finally:
            yield f'data: {{"content": "", "status": "ended"}}\n\n'

    return StreamingResponse(agent_event_stream(method='next_question', prompt=context_manager.get_user_current_question(uid).question, tone=tone), media_type="text/event-stream")