from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from ws_handlers import handle_audio_stream
from ai_handler import ai_handler
from interview_result import interview_result

app = FastAPI()
app.include_router(ai_handler, prefix="/ai", tags=["AI"])
app.include_router(interview_result, prefix="/result", tags=["Result"])

# @app.get("/")
# async def read_root():
#     return FileResponse('static/asr.html')

# 挂载static文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.websocket("/ws/asr/{user_id}")
async def websocket_endpoint_asr(websocket: WebSocket, user_id: str):
    await websocket.accept()
    await handle_audio_stream(websocket, user_id)