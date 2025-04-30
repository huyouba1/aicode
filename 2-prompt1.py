from langchain.prompts import PromptTemplate




if __name__ == '__main__':
    prompt_template = prompt_template = PromptTemplate.from_template(
        "给我讲一个关于{content}的{adjective}笑话"
    )

    result = prompt_template.format(content="猴子", adjective="冷")
    print(result)

