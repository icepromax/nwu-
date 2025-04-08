import ollama


# 定义一个聊天循环
def chat_with_ollama():
    print("欢迎使用 Ollama 本地问答系统！（输入 'exit' 退出）")

    # 聊天历史记录
    messages = []

    while True:
        user_input = input("你: ")
        if user_input.lower() == "exit":
            print("退出聊天。")
            break

        # 记录用户输入
        messages.append({"role": "user", "content": user_input})

        # 发送给 Ollama 进行对话
        response = ollama.chat(model='llama3:8b', messages=messages)

        # 获取 AI 回复
        ai_reply = response['message']['content']
        print("AI:", ai_reply)

        # 记录 AI 回复
        messages.append({"role": "assistant", "content": ai_reply})


# 运行聊天程序
chat_with_ollama()
