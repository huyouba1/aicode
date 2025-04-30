from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

# 加载环境变量
load_dotenv()

# 初始化模型
model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


chunks = []
for chunk in model.stream("天空是什么颜色？"):
    chunks.append(chunk)
    print(chunk.content,end='|',flush=True)
