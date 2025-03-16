from groq import Groq

# API 키 입력하는 곳
groq_api_key = "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"

#Groq 설정. 사이트에서 참고
class ChatBot:
    def __init__(self, engine: str = "llama3-8b-8192") -> None:
        self.model = engine
        self.client = Groq(api_key=groq_api_key)
        self.conversation_history = [
            {"role": "system", "content": "You will print out the lines of the game NPC from now on. I will give you the information and situation information of the NPC, so please make a comprehensive judgment and simply write down the lines that the NPC will do in one sentence in a large quotation mark."}
        ]  # 역할 설정

    def send_message(self, message: str) -> str:
        assistant_response = "" #초기화
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            assistant_response = completion.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
        except Exception as error:
            print("Error:", error)
        
        return assistant_response


def main():
    print("Welcome to ChatBot! Type 'quit' to exit.")
    chatbot = ChatBot()

    while True:
        user_input = input("화자: ")
        if user_input.lower() == "quit":
            break
        response = chatbot.send_message(user_input)
        print("ChatBot:", response)


if __name__ == "__main__":
    main()