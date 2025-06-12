from fastapi import FastAPI, WebSocket
from asr_handler import create_recognition
import asyncio

active_recognitions = {}

async def handle_audio_stream(websocket: WebSocket, user_id: str):
    if user_id in active_recognitions:
        await websocket.send_text("已有正在进行的识别任务")
        await websocket.close()
        return

    loop = asyncio.get_running_loop()
    try:
        recognition = create_recognition(websocket, loop)
        active_recognitions[user_id] = recognition
        recognition.start()
        # print(f"用户 {user_id} 的识别任务已启动")
        while True:
            data = await websocket.receive_bytes()
            # print(f"收到用户 {user_id} 的音频数据: {len(data)}")
            recognition.send_audio_frame(data)
    except Exception as e:
        print(f"WebSocket 错误")
        print(e, e.__class__, e.__traceback__)
    finally:
        recognition.stop()
        del active_recognitions[user_id]
        # print(f"用户 {user_id} 的识别任务已结束")