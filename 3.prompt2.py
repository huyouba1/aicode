from langchain.prompts import ChatPromptTemplate


if __name__ == '__main__':
    result1 = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一位人工智能助手，你的名字是{name}。"),
                ("human", "你好"),
                ("ai", "我很好，谢谢！"),
                ("human", "{user_input}"),
            ]
        ).format_messages(user_input="你的名字是什么。",name="小明")

    print(result1)