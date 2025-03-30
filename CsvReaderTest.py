from groq import Groq
import csv
from typing import List, Dict, Any

# API 키 입력하는 곳
groq_api_key = ""

#시나리오 리스트 저장용 DataClass
class SceneInfo:
    ScenarioText = []
    ScenarioOrder = []
    Npc1Info = []
    Npc2Info = []

class CsvReader:
    def __init__(self, file_path: str, list_columns: List[str] = None):
        self.file_path = file_path
        self.list_columns = list_columns if list_columns else []
        self.data = self._read_csv()
    
    def _read_csv(self) -> List[Dict[str, Any]]:
        #CSV 파일을 읽어 리스트의 딕셔너리 형태로 반환
        data = []           #새 리스트 생성
        with open(self.file_path, mode='r', encoding='utf-8') as file:
            for row in data:
                for col in self.list_columns:
                    if col in row and isinstance(row[col], str):
                        row[col] = row[col].strip('[]').split(';')
                        row[col] = [item.strip('"') for item in row[col] if item.strip()]
        return data
    
    def get_data(self) -> List[Dict[str, Any]]:
        #읽은 데이터 반환
        return self.data
    
    # 각 행(row)에 대해 주어진 조건 함수를 실행하여 조건을 만족하는 행만 반환
    def filter_rows(self, condition_func) -> List[Dict[str, Any]]:
        filtered_data = [row for row in self.data if condition_func(row)]
        return filtered_data
    
    # 특정 조건을 만족하는 행에서 특정 속성(column) 값만 리스트로 반환하는 함수
    def get_column_values(self, condition_func, column_name: str):
        return [row[column_name] for row in self.data if condition_func(row)]
    
def GetScenarioInfo(self):
    file_path = "DataFile\ScenarioInfo.csv"
    reader = CsvReader(file_path, list_columns=["ScriptList", "OrderList"])
    
    SceneInfo.ScenarioText = reader.filter_rows(lambda row: 'Sample Scenario' in row['ScenarioName'])

def GetNpcInfo(self):
    file_path = "DataFile\CharcterInfo.csv"
    reader = CsvReader(file_path, list_columns=["personality", "speech"])

    # 특정 조건에 맞는 행만 필터링
    SceneInfo.Npc1Info = reader.filter_rows(lambda row: 'NPC1' in row['name'])
    SceneInfo.Npc2Info = reader.filter_rows(lambda row: 'NPC2' in row['name'])

    # 결과 출력quit
    print("NPC1 List:", SceneInfo.Npc1Info)
    print("NPC2 List:", SceneInfo.Npc2Info)

# Groq 설정. 사이트에서 참고
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