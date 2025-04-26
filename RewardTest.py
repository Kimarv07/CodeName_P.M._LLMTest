from dotenv import load_dotenv
from crewai import Agent, Task, Crew
import json
from typing import List, Dict, Tuple, Any

# 환경변수 로드
load_dotenv()

#보상 편지 생성에 사용할 정보들
class Information:
    ScenarioDialogue:List[str] = []
    NpcData = List[Dict[str, Any]]

#JSON 리더기
#후에 DB 호출 방식으로 변경 예정
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
    
# 에이전트 정의

#성격 분석 Agent
Personality_Analyst = Agent(
    role = "Agent for identifying character personality",
    goal=f"",
    backstory="""
"""
)

#성격 분석 Task
Analyze_Personality = Task(
    description=f"""
    """,
    agent = Personality_Analyst
)

#상황 분석 Agent
Situation_Analyst = Agent(
    role = "Agent for analysis and summary of the situation",
    goal=f"",
    backstory="""
    """
)

#상황 분석 Task
Analyze_Situation = Task(
    description=f"""
    """,
    agent = Situation_Analyst
)

#편지 작성 Agent
Letter_Writer = Agent(
    role = "Agent for collect and analyze information and produce letter-type results",
    goal=f"",
    backstory="""
    """
)

#편지 작성 Task
Generate_Sentence = Task(
        description=f"""
    """,
    agent = Letter_Writer,
    context=[Analyze_Personality, Analyze_Situation]
)

#crew 설정
crew = Crew(
    agents=[Personality_Analyst, Situation_Analyst, Letter_Writer],
    tasks=[Analyze_Personality, Analyze_Situation, Generate_Sentence],
    verbose=False
)

result = crew.kickoff()