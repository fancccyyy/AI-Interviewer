from ai_caller import agent_callers
from user_context_singleton import context_manager
from config import QUESTIONS
import json
import re

def ai_procedure(uid: str, prompt: str, tone: str):
    """
    1. Say hello and ask the first question, using 'first_hello' agent
    2. Wait for the user to answer
    3. Generate the next question, using 'next_question' agent
    4. Wait for the user to answer
    5. Generate the final answer, using 'final_answer' agent
    """

def get_next_question(uid: str, tone:str):
    """
    Get next question based on user's progress
    """
    progress = context_manager.get_user_progress(uid)
    if progress is None:
        raise ValueError(f"User {uid} has no progress")
    
    current_qa = context_manager.get_user_current_question(uid)
    if current_qa is None:
        raise ValueError(f"User {uid} has no current question")

    print(f"done? {context_manager.is_interview_done(uid)}")
    if context_manager.is_interview_done(uid):
        raise ValueError(f"User {uid} has already done the interview")

    chunks = []
    interview_done = False
    
    print(progress.total_questions)
    print({"original_question": current_qa.question, "original_answer": current_qa.answer})
    if progress.current_question_type == "given":
        print("给定问题结束，进入追问模式")
        for chunk in agent_callers('more_questions', 
            json.dumps({"original_question": current_qa.question, "original_answer": current_qa.answer}), 
            tone):
            chunks.append(chunk)
            yield chunk
    elif progress.current_question_type == "probe":
        print("追问完毕，切换新问题")
        if progress.total_questions['probe'] >= len(QUESTIONS):
            for chunk in agent_callers('thats_all', 
                json.dumps({
                    "original_question": current_qa.question, 
                    "original_answer": current_qa.answer,
                }), 
                tone):
                chunks.append(chunk)
                yield chunk
            yield f'\n\n面试已结束，感谢您的参与。\n您的的面试记录已生成，[点击查看](/result/{uid})'
            interview_done = True
            context_manager.set_interview_done(uid)
            print("面试结束，打印全部问题和回答")
            qa_list = context_manager.get_user_qa(uid)
            for i, qa in enumerate(qa_list):
                print(f"第{i+1}个问题：{qa.question}，回答：{qa.answer}")
        else:
            for chunk in agent_callers('switch_question', 
                json.dumps({
                    "original_question": current_qa.question, 
                    "original_answer": current_qa.answer,
                    "new_question": QUESTIONS[progress.total_questions['probe']],
                }), 
                tone):
                chunks.append(chunk)
                yield chunk
    elif progress.current_question_type == "thats_all":
        interview_done = True
        print("面试结束，打印全部问题和回答")
        print(context_manager.get_user_qa_list(uid))
    else:
        raise ValueError(f"Unknown question type: {progress.current_question_type}")

    pattern = r'\*\*(.*?)\*\*'
    if not interview_done:
        try:
            plain_question = re.findall(pattern, "".join(chunks))[-1]
        except:
            plain_question = "".join(chunks)
        context_manager.start_new_question(uid, plain_question, "probe" if progress.current_question_type == "given" else "given")
