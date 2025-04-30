from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# from openai import OpenAI
import os

if __name__ == '__main__':
    load_dotenv()

    # client = OpenAI(
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    # )
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    output_parser = StrOutputParser()

    # 创建一个提示模板(prompt template)
    # 这里以对话模型的消息格式为例子，不熟悉openai对话模型消息格式，建议先学习OpenAI的API教程
    # 下面消息模板，定义两条消息，system消息告诉模型扮演什么角色，user消息代表用户输入的问题，这里用了一个占位符{input} 代表接受一个模版参数input。
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是世界级的技术专家"),
        ("user", "{input}")
    ])

    # 基于LCEL 表达式构建LLM链，lcel语法类似linux的pipeline语法，从左到右按顺序执行
    # 下面编排了一个简单的工作流，首先执行prompt完成提示词模板(prompt template)格式化处理， 然后将格式化后的prompt传递给llm模型执行，最终返回llm执行结果。
    chain  =  prompt | llm | output_parser
    # 调用LLM链并设置模板参数input,  invoke会把调用参数传递给prompt提示模板，开始chain定义的步骤开始逐步执行。
    result = chain.invoke({"input": "帮我写一篇关于AI的技术文章，100个字"})
    print(result)

    # completion = client.chat.completions.create(
    #     model="qwen-plus",
    #     messages=[
    #         {"role": "system", "content": "你是世界级的技术专家"},
    #         {"role": "user", "content": "帮我写一篇关于AI的技术文章，100个字"}
    #     ]
    # )
    

    # print( completion.model_dump_json())

