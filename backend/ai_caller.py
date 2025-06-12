import os
from http import HTTPStatus
from dashscope import Application
from config import DASHSCOPE_AI_AGENTS_APP_ID, DASHSCOPE_API_KEY
from time import sleep
import sys

def agent_callers(method: str, prompt: str, tone: str):
    if method not in DASHSCOPE_AI_AGENTS_APP_ID:
        raise ValueError(f"Invalid method: {method}")
    
    response_iterator = Application.call(
        api_key=DASHSCOPE_API_KEY,
        app_id=DASHSCOPE_AI_AGENTS_APP_ID[method],
        prompt=prompt,
        biz_params = {
            "user_prompt_params": {
                "tone": tone,
            }
        },
        stream=True,
        incremental_output=True,
    )

    for chunk in response_iterator: # 迭代原始的响应迭代器
        if chunk.status_code != HTTPStatus.OK:
            # 处理错误情况，例如记录日志、抛出异常或通知客户端
            # 您可以选择在这里 yield 一个错误指示，或者直接 raise 异常
            # print(f"Error: {chunk.status_code} - {chunk.message}") 
            # yield f"Error: {chunk.status_code} - {chunk.message}" # 示例：yield 错误信息
            raise Exception(f"Stream error: Code {chunk.status_code}, Message: {chunk.message}, Request ID: {chunk.request_id}") # 或者直接抛出异常
            # break # 如果选择 yield 错误，可能需要 break
        else:
            # 假设每个 chunk 都有 output 和 text 属性
            if hasattr(chunk, 'output') and hasattr(chunk.output, 'text'):
                yield chunk.output.text # 使用 yield 返回每个增量结果
            # 根据实际的 chunk 结构，您可能需要调整如何访问文本内容
    
    # 当迭代完成时，生成器函数会自动结束
    # 不需要显式的 return None，除非您想在最后 yield 一个特定的结束标记

def myprint(text):
    sys.stdout.write(text)
    sys.stdout.flush()
    sleep(0.1)

if __name__ == '__main__':
    # 调用 agent_callers 会返回一个生成器
    stream_output = agent_callers('first_hello', '你最近完成的一件最有成就感的事是什么？你在其中扮演了什么角色？', '专业')
    
    # 迭代生成器以获取流式数据
    full_response = ""
    buffer = ""
    state = "FORWARDING"  # 可选: FORWARDING / CAPTURING / SUSPECTING
    capture_buffer = ""
    suspect_buffer = ""
    try:
        for text_chunk in stream_output:
            buffer += text_chunk
            # myprint(f"buffer: {buffer}")

            while True:
                if state == "FORWARDING":
                    q_pos = buffer.find("[")
                    if q_pos == -1:
                        # 没找到 [，全部转发
                        myprint(buffer)
                        buffer = ""
                        break
                    else:
                        # myprint(f'found at {q_pos}]')
                        # 可疑模式，多读取一份chunk看能否拼出完整的[Q]
                        state = "SUSPECTING"
                        q_pos = buffer.find("[Q]")
                        if q_pos == 1:
                            # 发送 [Q] 前面的部分
                            myprint(buffer[:q_pos])
                            buffer = buffer[q_pos + 3:]  # 截断 buffer 到 [Q] 之后
                            state = "CAPTURING"
                elif state == "SUSPECTING":
                    q_pos = buffer.find("[Q]")
                    if q_pos == -1:
                        # 没找到 [Q]，解除嫌疑
                        myprint(buffer)
                        state = "FORWARDING"
                        buffer = ""
                    else:
                        # 找到 [Q]，截断 buffer 到 [Q] 之后
                        myprint(buffer[:q_pos])
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
        print("\n--- End of Stream ---")
        # print(f"\nFull assembled response: {full_response}")
    except Exception as e:
        print(f"\nAn error occurred during streaming: {e}")