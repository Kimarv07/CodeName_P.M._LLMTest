from groq import Groq
import json
from typing import List, Dict, Tuple, Any
import re

# API 키 입력하는 곳
groq_api_key = "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"

#시나리오 리스트 저장용 DataClass
class SceneInfo:
    ScenarioText = []
    ScenarioOrder = []
    NpcData =  List[Dict[str, Any]]

    LLMPrompt = ""

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
        self.promptGuide = "You will generate the dialogue for multiple NPCs. Each NPC's personality and the situation will be given. Use only the NPCs that appear in the conversation to determine their speech. When you talk about the content, use colloquial as if you were actually speaking, and organize the sentence into 1 sentence with words that are easy to understand. Create a conversation for each step of the 'Scenario Progress Order'. Instead of continuing the conversation on your own, make sure you can only create the conversation within the given guide."
        self.conversation_history = [
            {"role": "system", "content": self.promptGuide}
        ]  # 역할 설정
        self.dialogue_history = []  # 대화 저장 리스트
        self.response_data : List[Tuple[str, str]] = []  # 대화 저장 리스트

    def store_response(self, speaker: str, response: str):
        #LLM의 응답을 발화자 정보와 함께 저장
        self.response_data.append({"speaker": speaker, "response": response})  

    def store_conversation(self, speaker: str, dialogue: str):
        #NPC의 대화 내용을 리스트에 저장
        self.dialogue_history.append({"speaker": speaker, "dialogue": dialogue})

    def get_full_response(self):
        #저장된 전체 대화 기록을 반환
        return self.response_data
    
    def set_promptMessage(self):
        script_length = len(SceneInfo.ScenarioText)
        
        if len(SceneInfo.NpcData) == 0 or script_length == 0:
            print("NPC 데이터 또는 시나리오가 없습니다.")
            return ""

        # ScenarioOrder에 등장하는 NPC만 추출
        used_npc_names = set(SceneInfo.ScenarioOrder)
        filtered_npc_data = {npc["name"]: npc for npc in SceneInfo.NpcData if npc["name"] in used_npc_names}

        # 대화 기록 생성
        dialogue_sequence = []
        for i in range(script_length):
            speaker_name = SceneInfo.ScenarioOrder[i]  # 현재 대화의 발화자
            situation = SceneInfo.ScenarioText[i]  # 해당 발화자의 상황 설명

            # 발화자 정보 가져오기
            speaker_info = filtered_npc_data.get(speaker_name, {"personality": "알려지지 않음"})  
            speaker_personality = speaker_info.get("personality", "알려지지 않음")

            # 대화 문장 추가
            dialogue = f"{speaker_name}({speaker_personality}): {situation}"
            dialogue_sequence.append(dialogue)

            # 대화 저장
            self.store_conversation(speaker_name, situation)

        # 프롬프트 메시지 생성
        prompt_message = f"""
        This is the conversation between NPCs in the current scenario.

        current situation: {" ".join(SceneInfo.ScenarioText)}  
        Scenario Progress Order: {" → ".join(SceneInfo.ScenarioOrder)}  

        conversation:
        {'\n'.join(dialogue_sequence)}

        """.strip()

        return prompt_message

    def split_response_with_speaker(self, response: str) -> List[Tuple[str, str]]:
        """
        LLM 응답을 개별 대사 단위로 리스트로 변환하면서,
        NPC 발화자 정보를 함께 저장.

        반환 형식: [(NPC 이름, 대사), (NPC 이름, 대사), ...]
        """
        dialogue_list = []
        
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue  # 빈 줄은 무시

            # 발화자 추출 (예: "NPC1: 대사" -> "NPC1" 분리)
            pattern = r"^([A-Za-z0-9가-힣]+)\s*(?:\(\[[^\]]*\]\))?:\s*(.*)"
            match = re.match(pattern, line)
            if match:
                speaker = match.group(1)  # NPC 이름
                dialogue = match.group(2)  # 실제 대사
                dialogue_list.append((speaker, dialogue))
            else:
                dialogue_list.append(("Unknown NPC", line))  # 발화자 인식 실패 시
        
        return dialogue_list
    
    def reset_conversation_history(self):
        self.conversation_history = [
            {"role": "system", "content": self.promptGuide}
        ]

    def send_message(self) -> str:
        self.LLMPrompt = self.set_promptMessage()
        assistant_response = "" #초기화
        self.conversation_history.append({"role": "user", "content": self.LLMPrompt})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=1,
                max_completion_tokens=1024,
                top_p=0.7,
                stream=False,
                stop=None,
            )
            
            assistant_response = completion.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
            # 응답을 분석하여 (NPC, 대사) 리스트로 변환
            parsed_response = self.split_response_with_speaker(assistant_response)
            
            # 대화 데이터에 추가
            self.response_data.extend(parsed_response)

        except Exception as error:
            print("Error:", error)
        
        return assistant_response
    
    def save_conversation_to_json(self, filename="conversation.json"):
        """
        대화 데이터를 JSON 파일로 저장
        """
        # 필터링: 'Unknown NPC'가 아닌 데이터만 저장
        filtered_data = filtered_data = [{"speaker": entry[0], "text": entry[1]} for entry in self.response_data if entry[0] != "Unknown NPC"]

        data = {"dialogues": filtered_data}

        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)  # UTF-8로 저장하여 한글 깨짐 방지

        print(f"✅ 대화가 {filename} 파일로 저장되었습니다.")

if __name__ == "__main__":
    NpcReader = JSONReader("DataFile\CharacterInfo_J.json", list_columns=["personality", "speech"])

    # 전체 NPC 데이터 출력
    SceneInfo.NpcData = NpcReader.get_data()
    print("전체 데이터:", SceneInfo.NpcData)

    ScenarioReader = JSONReader("DataFile\ScenarioInfo_J.json", list_columns=["ScriptList","OrderList"])
    ScenarioData = ScenarioReader.get_data()
    SceneInfo.ScenarioText = (ScenarioReader.get_column_values(lambda row: row["ScenarioName"] == "Sample Scenario", "ScriptList")[0])
    print(SceneInfo.ScenarioText)
    SceneInfo.ScenarioOrder = (ScenarioReader.get_column_values(lambda row: row["ScenarioName"] == "Sample Scenario", "OrderList")[0])

    chatbot = ChatBot()
    chatbot.send_message()
    conversation_data = chatbot.get_full_response()
    print(conversation_data)
    chatbot.save_conversation_to_json()