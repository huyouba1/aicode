from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os,asyncio
# 加载环境变量
load_dotenv()

# 初始化模型
model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

prompt = ChatPromptTemplate.from_template("给我讲一个关于{topic}的笑话")
parser = StrOutputParser()
chain = prompt | model | parser

# 使用同步方式调用，避免在非异步环境中使用async
def stream_joke(topic):
    for chunk in chain.stream({"topic": topic}):
        print(chunk, end="|", flush=True)

# 调用函数
if __name__ == "__main__":
    stream_joke("鹦鹉")

