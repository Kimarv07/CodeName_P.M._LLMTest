from dotenv import load_dotenv
from crewai import Agent, Task, Crew
import json
from typing import List, Dict, Tuple, Any

# 환경변수 로드
load_dotenv()

#보상 편지 생성에 사용할 정보들
class Information:
    ScenarioDialogue: List[str] = [] #시나리오 다이얼로그
    NpcData: List[Dict[str, Any]] = [] #NPC 정보 데이터
    ResponseData: str = ""

#JSON 리더기
#후에 DB 호출 방식으로 변경 예정
class JSONReader:
    def __init__(self, file_path: str, list_columns: List[str] = None):
        """
        JSON 파일을 읽어들이고 지정된 문자열 컬럼을 리스트로 변환하는 Reader 클래스.
        
        :param file_path: JSON 파일 경로
        :param list_columns: 문자열로 저장된 리스트 형식 컬럼들 (예: '["a", "b"]' -> ['a', 'b'])
        """
        self.file_path = file_path
        self.list_columns = list_columns if list_columns else []
        self.data = self._read_json()

    def _read_json(self) -> List[Dict[str, Any]]:
            """
            JSON 파일을 읽어 리스트 형태로 반환.
            - 단일 딕셔너리인 경우에도 리스트로 변환하여 통일성 유지.
            - list_columns 에 대해 문자열을 리스트로 파싱 처리.
            """
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)  # JSON 파싱

            # JSON이 딕셔너리인 경우 -> 리스트로 변환하여 통일된 처리
            if isinstance(data, dict):
                data = [data]
        
            # 리스트 형식이지만 요소가 딕셔너리가 아닌 경우 오류 발생
            if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
                raise ValueError(
                    f"잘못된 JSON 구조입니다: '{self.file_path}'는 딕셔너리들의 리스트여야 합니다."
            )

            # list_columns에 지정된 컬럼들을 문자열에서 리스트로 변환
            for row in data:
                for col in self.list_columns:
                    if col in row and isinstance(row[col], str):
                        # 문자열 형태로 저장된 리스트 처리: ["a";"b"] 또는 [a;b] 형태 대응
                        row[col] = row[col].strip('[]').split(';')
                        row[col] = [item.strip('" ').strip("'") for item in row[col] if item.strip()]

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
    goal=f"Your goal is to identify the character's character so that you can use it for future writing.",
    backstory="""
    You are a writer who has to transfer and write to a particular character.
    It has the task of writing the emotions and speech of the character as they are.
    To do this, you have to interpret the character's personality with the given information and make it your own.
    """
)

#성격 분석 Task
Analyze_Personality = Task(
    description=f"""
    Analyze the information in 'NpcData' and convert it into information that can be used for prompts, and store it in memory for use in other tasks later.

    The 'NpcData'is here: {Information.NpcData}

    Make sure the final result is a prompt message that can be used for some LLM.
    Don't type any additional messages, but only print out the answers.
    """,
    agent = Personality_Analyst,
    expected_output = "Only print out the answer"
)

#상황 분석 Agent
Situation_Analyst = Agent(
    role = "Agent for analysis and summary of the situation",
    goal=f"Read the given dialog and analyze what the situation is and summarize it simply.",
    backstory="""
    You read the game's conversation log and simply organize it.
    Read the content and figure out what each character did and what emotions they had.
    """
)

#상황 분석 Task
Analyze_Situation = Task(
    description=f"""
    You should check the given game 'dialogue' to analyze and organize what happened. Information can be used for prompts, and store it in memory for use in other tasks later.

    'dialogue' is here: {Information.ScenarioDialogue}

    Make sure the final result is a prompt message that can be used for some LLM.
    Don't type any additional messages, but only print out the answers.
    """,
    agent = Situation_Analyst,
    expected_output = "Only print out the answer"
)

#사용자 답변 분석 Agent
Response_Analyst = Agent(
    role = "Agent for analyze answers and check if the situation changes",
    goal=f"The goal is to check the given situation and advice and to see which direction the situation will develop.",
    backstory="""
    You should look at the given situation dialogs and user advice and make predictions about what will happen later.
    You should determine what good results the user's answers will bring, become a counselor, and make a friendly prediction.
    """
)

#사용자 답변 분석 Task
Analyze_Response = Task(
    description=f"""
    You should check the 'answers' and 'situation' information provided by the user and predict the positive impact that can occur in the future.

    Here is the 'situation': {Information.ScenarioDialogue}
    And, Here is the 'answer': {Information.ResponseData}

    Make sure the final result is a prompt message that can be used for some LLM.
    Don't type any additional messages, but only print out the answers.
    """,
    agent = Response_Analyst,
    context=[Analyze_Situation],
    expected_output = "Only print out the answer"
)

#편지 작성 Agent
Letter_Writer = Agent(
    role = "Agent for collect and analyze information and produce letter-type results",
    goal=f"You have to write a letter-type piece by combining all the information of the given situation, the character to follow, and the information that predicts what will happen.",
    backstory="""
    It will teach you the personality and way of speaking so that you can imitate the person's way of speaking. Then, you can imitate the way you speak and write a letter according to the situation you understand.
    """
)

#편지 작성 Task
Generate_Sentence = Task(
    description=f"""
    You have to write a letter. But you have to know that you have to pretend to be someone else and use it.
    It will teach you the personality and way of speaking so that you can imitate the person's way of speaking.

    The information containing the characters that need to be imported is as follows.
    Here is the NPC Data: {Information.NpcData}

    It is important to keep in mind that the situation information to be grasped is as follows, and that changes after that situation must be predicted.
    Here is the situation Data: {Information.ScenarioDialogue}

    Finally, the future message should be included in the content by looking at the following answers to predict how the situation will flow positively.
    You should check the situation above and think about what will change afterward if you take action according to the answer. 
    Here is the answer data: {Information.ResponseData}

    You can write in the form of a letter by combining all the above data.
    """,
    agent = Letter_Writer,
    context=[Analyze_Personality, Analyze_Situation, Analyze_Response],
    expected_output = "Only print out the answer"
)


if __name__ == "__main__":
    NpcReader = JSONReader(r"DataFile\CharacterInfo_J.json", list_columns=["personality", "speech"]) 
    DialogReader = JSONReader(r"conversation.json")
    ResponseReader = JSONReader(r"child_conflict_analysis_result.json", list_columns=["child_response"])

    #기본 정보 설정
    #Information.NpcData = NpcReader.get_data()
    Information.NpcData = NpcReader.get_data()
    print(Information.NpcData)
    Information.ScenarioDialogue = DialogReader.get_data()
    print(Information.ScenarioDialogue)
    Information.ResponseData = ResponseReader.get_data()
    print(Information.ResponseData)

    #crew 설정
    crew = Crew(
    agents=[Personality_Analyst, Situation_Analyst, Response_Analyst, Letter_Writer],
    tasks=[Analyze_Personality, Analyze_Situation, Analyze_Response, Generate_Sentence],
    verbose=False
    )
    
    crew.kickoff()
    
    print(Generate_Sentence.output)

    with open("RewardLetter.json", "w", encoding="utf-8") as json_file:
        json.dump(Generate_Sentence.output.model_dump(), json_file, indent=4, ensure_ascii=False)