from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()
@app.get("/stream/question")
async def stream_question():
    async def generate():
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", AI_STREAM_URL) as response:
                buffer = ""
                state = "FORWARDING"  # 可选: FORWARDING / CAPTURING
                capture_buffer = ""

                async for chunk in response.aiter_text():
                    buffer += chunk

                    while True:
                        if state == "FORWARDING":
                            q_pos = buffer.find("[Q]")
                            if q_pos == -1:
                                # 没找到 [Q]，全部转发
                                yield buffer
                                buffer = ""
                                break
                            else:
                                # 发送 [Q] 前面的部分
                                yield buffer[:q_pos]
                                buffer = buffer[q_pos + 3:]  # 截断 buffer 到 [Q] 之后
                                state = "CAPTURING"
                        elif state == "CAPTURING":
                            end_pos = buffer.find("[/Q]")
                            if end_pos == -1:
                                # 还没收到 [/Q]，继续缓存
                                capture_buffer += buffer
                                buffer = ""
                                break
                            else:
                                # 收到 [/Q]，提取入库内容
                                capture_buffer += buffer[:end_pos]
                                db_content = capture_buffer.strip()
                                print("✅ 入库内容:", db_content)

                                # 重置状态
                                buffer = buffer[end_pos + 4:]  # 截断到 [/Q] 之后
                                capture_buffer = ""
                                state = "FORWARDING"
    return StreamingResponse(generate(), media_type="text/event-stream")