# AI-Interviewer
This is a simple AI interviewer that conducts AI behavioral interviews by voice, originally for internship task of Kora

## Frameworks and AI Model
1. Backend using `Python` + `Fastapi`, frontend using `React` + `AntDesign`. Special thanks to these brilliant open source projects.
2. AI agents and AI speech-to-text using [阿里云的大模型服务平台百炼](https://bailian.console.aliyun.com/?tab=doc#/doc)
3. The AI model behind is `qwen-plus-2025-04-28-128K`, part of Qwen3 Series

## Features
1. The process is broken into four parts: Initial greeting -> Ask a given question -> Probe further based on QA -> Switch to another given question, thus 4 agents are created and working separately, so each model can better focus on its own job
2. A not-so-bad UI design, at least I believe it is.
3. Speech-to-text is AI powered, with high quailty and auto punctuation
4. You can change the tone for AI interviewr whenever you wish.
5. By the end of the interview process, you'll get a result page for sharing and reviewing.
6. User input is purified, so do not attempt to XSS it.
7. More you can explore by yourself😎

## How to use?
1. git clone the project
2. Replace the API secret key and AppID in backend/Config.py with your own. More info at [阿里云的大模型服务平台百炼](https://bailian.console.aliyun.com/?tab=doc#/doc)
3. Launch the app🚀, either by directly running or by docker (Dockerfile is included)
