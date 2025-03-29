from groq import Groq
import csv
from typing import List, Dict, Any
from pathlib import Path

# API 키 입력하는 곳
groq_api_key = ""

class CsvReader:
    def __init__(self, file_path: str, list_columns: List[str] = None, delimiter: str = ','):
        self.file_path = file_path
        self.list_columns = list_columns if list_columns else []
        self.delimiter = delimiter
        self.data = self._read_csv()
    
    def _read_csv(self) -> List[Dict[str, Any]]:
        #CSV 파일을 읽어 리스트의 딕셔너리 형태로 반환
        data = []           #새 리스트 생성
        with open(self.file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            for row in reader:
                for col in self.list_columns:
                    if col in row:
                        row[col] = row[col].strip('[]').split(';')
                        row[col] = [item.strip('"') for item in row[col] if item.strip()]
                data.append(row)
        return data
    
    def get_data(self) -> List[Dict[str, Any]]:
        #읽은 데이터 반환
        return self.data
    
    def filter_rows(self, condition_func) -> List[Dict[str, Any]]:
        # 각 행(row)에 대해 주어진 조건 함수를 실행하여 조건을 만족하는 행만 반환
        filtered_data = [row for row in self.data if condition_func(row)]
        return filtered_data



#Groq 설정. 사이트에서 참고
class ChatBot:
    def __init__(self, engine: str = "llama3-8b-8192") -> None:
        self.model = engine
        self.client = Groq(api_key=groq_api_key)
        self.conversation_history = [
            {"role": "system", "content": "You will print out the lines of the game NPC from now on. I will give you the information and situation information of the NPC, so please make a comprehensive judgment and simply write down the lines that the NPC will do in one sentence in a large quotation mark."}
        ]  # 역할 설정

    def set_message(self):
        pass

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
    file_path = "CSV\CharcterInfo.csv"
    reader = CsvReader(file_path, list_columns=["personality", "speech"])
    data = reader.get_data()
    print(data)

     # 특정 조건에 맞는 행만 필터링 (예: tags가 'NPC1'인 행만 찾기)
    filtered_rows = reader.filter_rows(lambda row: 'NPC1' in row['name'])
    
    # 필터링된 데이터를 다른 리스트에 저장
    other_list = [row for row in filtered_rows]

    # 결과 출력
    print("Filtered Rows:", filtered_rows)
    print("Other List:", other_list)

    print("Welcome to ChatBot! Type 'quit' to exit.")
    chatbot = ChatBot()

    while True:
        user_input = input("화자: ")
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "next":
            pass
        response = chatbot.send_message(user_input)
        print("ChatBot:", response)
        

if __name__ == "__main__":
    main()