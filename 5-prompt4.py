from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import HumanMessage

if __name__ == '__main__':
    prompt_template = ChatPromptTemplate.from_messages([
        ("system","You are a helpful assistant"),
        MessagesPlaceholder("msg")
    ])
    result = prompt_template.invoke({"msg":[HumanMessage("Hello, how can I help you?")]})
    print(result)


    prompt_template2 = ChatPromptTemplate.from_messages([
        ("system","You are a helpful assistant"),
        ("placeholder","{msg}")
    ])
    
    print("==========")
    result2 = prompt_template2.invoke({"msg":[HumanMessage("Hello, how can I help you?")]})
    print(result2)