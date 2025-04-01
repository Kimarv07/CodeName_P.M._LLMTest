from groq import Groq
import json
from typing import List, Dict, Any

# API 키 입력하는 곳
groq_api_key = ""

#시나리오 리스트 저장용 DataClass
class SceneInfo:
    ScenarioText = []
    ScenarioOrder = []
    Npc1Info = []
    Npc2Info = []

    LLMPrompt = []

class JSONReader:
    def __init__(self, file_path: str, list_columns: List[str] = None):
        """
        JSON 파일을 읽는 리더 클래스
        :param file_path: JSON 파일 경로
        :param list_columns: 리스트 형식으로 변환할 컬럼 이름 리스트 (필요할 경우 사용)
        """
        self.file_path = file_path
        self.list_columns = list_columns if list_columns else []
        self.data = self._read_json()
    
    def _read_json(self) -> List[Dict[str, Any]]:
        """JSON 파일을 읽어 리스트의 딕셔너리 형태로 반환"""
        with open(self.file_path, mode='r', encoding='utf-8') as file:
            data = json.load(file)  # JSON 파일을 파싱하여 리스트/딕셔너리로 변환

        # 특정 컬럼을 리스트로 변환 (필요할 경우)
        for row in data:
            for col in self.list_columns:
                if col in row and isinstance(row[col], str):
                    row[col] = row[col].strip('[]').split(';')
                    row[col] = [item.strip('"') for item in row[col] if item.strip()]
        return data

    def get_data(self) -> List[Dict[str, Any]]:
        """읽은 데이터를 반환"""
        return self.data

    def filter_rows(self, condition_func) -> List[Dict[str, Any]]:
        """주어진 조건에 맞는 행을 필터링하여 반환"""
        return [row for row in self.data if condition_func(row)]
    
    def get_column_values(self, condition_func, column_name: str):
        """
        특정 조건을 만족하는 행에서 특정 속성(column) 값만 리스트로 반환하는 함수
        :param condition_func: 특정 행을 선택하는 조건 함수
        :param column_name: 가져오고 싶은 속성 이름
        :return: 조건을 만족하는 행들의 특정 속성 값 리스트
        """
        return [row[column_name] for row in self.data if condition_func(row)]

# Groq 설정. 사이트에서 참고
class ChatBot:
    def __init__(self, engine: str = "llama3-8b-8192") -> None:
        self.model = engine
        self.client = Groq(api_key=groq_api_key)
        self.conversation_history = [
            {"role": "system", "content": "You will print out the lines of the game NPC from now on. I will give you the information and situation information of the NPC, so please make a comprehensive judgment and simply write down the lines that the NPC will do in one sentence in a large quotation mark."}
        ]  # 역할 설정

    def set_message(self, CurSceneNum:int):
        scriptlength = len(SceneInfo.ScenarioText)

        if CurSceneNum > scriptlength:
            print("Script is End.")
            return
        SceneInfo.LLMPrompt.append({})



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

if __name__ == "__main__":
    reader = JSONReader("DataFile\CharacterInfo_J.json", list_columns=["personality", "OrderList"])

    # 전체 데이터 출력
    data = reader.get_data()
    print("전체 데이터:", data)

    # 특정 조건: id가 "1"인 행에서 "tags" 값만 가져오기
    NPC1_Info = reader.get_column_values(lambda row: row["name"] == "NPC1", "personality")
    print("NPC1 infomation:", NPC1_Info)
    if NPC1_Info:
        for personality in NPC1_Info[0]:
            print(personality)