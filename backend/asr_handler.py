from dashscope import audio
from dashscope.audio.asr import Recognition
from asr_callback import RecognitionCallbackHandler
from config import MODEL_NAME, AUDIO_FORMAT, SAMPLE_RATE
from init import init_dashscope_api_key
import asyncio

def create_recognition(websocket, loop):
    init_dashscope_api_key()
    callback = RecognitionCallbackHandler(websocket, loop)
    recognition = Recognition(
        model=MODEL_NAME,
        format=AUDIO_FORMAT,
        sample_rate=SAMPLE_RATE,
        semantic_punctuation_enabled=False,
        callback=callback
    )
    return recognition