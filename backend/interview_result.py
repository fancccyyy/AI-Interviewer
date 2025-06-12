from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from user_context_singleton import context_manager  
import json

interview_result = APIRouter()

# 挂载静态文件和模板
# interview_result.mount("/result", StaticFiles(directory="./templates"), name="templates")
templates = Jinja2Templates(directory="templates")

# 模拟面试数据
# test_interview_data = [
#     {
#         "id": 1,
#         "question": "请简单介绍一下你自己我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈",
#         "answer": "我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈"
#     },
#     {
#         "id": 2,
#         "question": "你最大的技术优势是什么？",
#         "answer": "我擅长快速学习新技术并应用到实际项目中，最近主导了公司微服务架构的迁移我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈"
#     },
#     {
#         "id": 3,
#         "question": "如何处理团队中的意见分歧？",
#         "answer": "我会组织技术评审会议，让各方充分表达观点，然后基于数据和最佳实践做出决策我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈我是一名有五年经验的全栈工程师，专注于Python和JavaScript技术栈"
#     }
# ]

# @interview_result.get("/test")
# async def test_read_interview(request: Request):
#     interview_data = test_interview_data

#     # 将数据转换为JSON字符串用于前端渲染
#     interview_json = json.dumps(interview_data)
    
#     return templates.TemplateResponse(
#         "interview_done.html",
#         {"request": request, "interview_data": interview_data, "interview_json": interview_json}
#     )

@interview_result.get("/{uid}")
async def read_interview(request: Request, uid: str):
    qa_list = context_manager.get_user_qa(uid)
    if not qa_list:
        raise HTTPException(status_code=404, detail="Interview data not found")

    interview_data = [
        {
            "id": i + 1,
            "question": qa.question,
            "answer": qa.answer,
        }
        for i, qa in enumerate(qa_list)
    ]

    # 将数据转换为JSON字符串用于前端渲染
    interview_json = json.dumps(interview_data)
    
    return templates.TemplateResponse(
        "interview_done.html",
        {"request": request, "interview_data": interview_data, "interview_json": interview_json}
    )

'''
# 待完成：MD下载导出
@interview_result.get("/download-md/{uid}")
def download_md(uid: str):
    qa_list = context_manager.get_user_qa(uid)
    if not qa_list:
        raise HTTPException(status_code=404, detail="Interview data not found")
    
    # 生成Markdown内容
    md_content = "# 面试记录\n\n"
    for qa in qa_list:
        md_content += f"## {qa.question}\n\n{qa.answer}\n\n---\n\n"

    # 生成文件
    with open(f"./files/interview_result_{uid}.md", "w") as f:
        f.write(md_content)

    # 返回文件
    return FileResponse(f"./files/interview_result_{uid}.md", filename=f"interview_result.md")

@interview_result.get("/download-md")
def download_md():
    qa_list = test_interview_data
    
    # 生成Markdown内容
    md_content = "# 面试记录\n\n"
    for qa in qa_list:
        md_content += f"## {qa.question}\n\n{qa.answer}\n\n---\n\n"

    # 生成文件
    with open(f"./files/interview_result_{uid}.md", "w") as f:
        f.write(md_content)

    # 返回文件
    return FileResponse(f"./files/interview_result_{uid}.md", filename=f"interview_result.md")
'''