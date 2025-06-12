import asyncio
from fastapi import WebSocket
from dashscope.audio.asr import RecognitionCallback

class RecognitionCallbackHandler(RecognitionCallback):
    def __init__(self, websocket: WebSocket, loop):
        self.websocket = websocket
        self.loop = loop

    def on_open(self):
        print("Recognition 打开")

    def on_close(self):
        print("Recognition 关闭")

    def on_complete(self):
        print("识别完成")

    def on_error(self, message):
        print('Recognition error:', message.message)

    def on_event(self, result):
        try:
            sentence = result.get_sentence()
            # print(f"收到识别结果: {sentence}")
            if 'text' in sentence:
                text = sentence['text']
                is_end = result.is_sentence_end(sentence)
                full_result = {
                    "text": text,
                    "is_end": is_end,
                    "request_id": result.get_request_id(),
                    "usage": result.get_usage(sentence),
                    "raw": sentence
                }
                # print(f"发送识别结果: {full_result}")
                asyncio.run_coroutine_threadsafe(self.websocket.send_json(full_result), self.loop)
        except Exception as e:
            print(f"发送识别结果失败: {e}")