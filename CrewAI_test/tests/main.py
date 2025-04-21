from dotenv import load_dotenv
from crewai import Agent, Task, Crew
import re
import statistics
import time
import json

# 환경 변수 로드
load_dotenv()

# 사용자 입력
prompt_text = """
You have studied the countries that participated in the World Cup during social studies class. 
Your team decided to research Japan. 
Everyone divided their roles, and after school, you all gathered at your house to continue the research.
However, there is one problem. One member of your group never participates and only plays around. 
This student is just an ordinary acquaintance to you, but other group members also seem dissatisfied. 
However, if you tell this student their mistake, they might get angry and start a fight.

What would you do in this situation?
"""
print(prompt_text)

conflict_response = input("Write down who is in conflict: ")
cause_response = input("Write down the cause of the conflict: ")
subject_response = input("Write down what the subject of conflict is: ")
child_response = input("Enter the child's proposed resolution method: ")

#답변 기준(DB에서 받아올 예정)

Recap={"""The child and their group are researching Japan for a class project.  
    One member consistently avoids participating and plays around.  
    Other members are frustrated.  
    The child knows this student only as an acquaintance.  
    Direct confrontation may lead to a fight."""}

Analyse_standard_A={"""Because habits need to be fixed, I will say it no matter what, even if it means fighting."""}
Analyse_standard_B={"""Because I don't like not fighting with friends, I will just ignore it."""}
Analyse_standard_C={"""I will do it instead of my friend."""}
Analyse_standard_D={"""I will calmly persuade the child to avoid fighting"""}
Analyse_conflict={"NPC1 and NPC2"}
Analyse_cause={"What should I do to a friend who is playing with no group activities?"}
Analyse_subject={"One member of the class project team didn't do any activities."}

# 결과 저장용 딕셔너리
scores = {"A": [], "B": [], "C": [], "D": [],  "S": []}
# 성향 확인 저장용 딕셔너리
social_result = {"So1": [], "So2": [], "So3": [], "So4": [],  "So5": []}

# 5번 반복 실행
for i in range(3):
    print(f"\n--- Run {i+1} ---")
    start = time.time()

    # 에이전트 정의
    Analyst_A = Agent(
        role="Senior Sentence Sentiment Analyst_A",
        goal=f"Determine how similar the child's proposed resolution method is to '{Analyse_standard_A}' and express the similarity as a percentage (rounded to one decimal place).",
        backstory="""You are an analyst who observes specific conflict situations and evaluates the resolution methods provided by children.
    Your role is to assess how similar a child's proposed resolution method is to the given target resolution,
    not by direct sentence matching but by comparing the **nature** of the resolution strategy itself.
    You must express the similarity as a percentage, rounded to one decimal place.""",
        verbose=False,
        allow_delegation=False,
    )

    Analyst_B = Agent(
        role="Senior Sentence Sentiment Analyst_B",
        goal=f"Determine how similar the child's proposed resolution method is to '{Analyse_standard_B}' and express the similarity as a percentage (rounded to one decimal place).",
        backstory="""You are an analyst who observes specific conflict situations and evaluates the resolution methods provided by children.
        Your role is to assess how similar a child's proposed resolution method is to the given target resolution,
        not by direct sentence matching but by comparing the **nature** of the resolution strategy itself.
        You must express the similarity as a percentage, rounded to one decimal place.""",
        verbose=False,
        allow_delegation=False,
    )

    Analyst_C = Agent(
        role="Senior Sentence Sentiment Analyst_C",
        goal=f"Determine how similar the child's proposed resolution method is to '{Analyse_standard_C}' and express the similarity as a percentage (rounded to one decimal place).",
        backstory="""You are an analyst who observes specific conflict situations and evaluates the resolution methods provided by children.
        Your role is to assess how similar a child's proposed resolution method is to the given target resolution,
        not by direct sentence matching but by comparing the **nature** of the resolution strategy itself.
        You must express the similarity as a percentage, rounded to one decimal place.""",
        verbose=False,
        allow_delegation=False,
    )

    Analyst_D = Agent(
        role="Senior Sentence Sentiment Analyst_D",
        goal=f"Determine how similar the child's proposed resolution method is to '{Analyse_standard_D}' and express the similarity as a percentage (rounded to one decimal place).",
        backstory="""You are an analyst who observes specific conflict situations and evaluates the resolution methods provided by children.
        Your role is to assess how similar a child's proposed resolution method is to the given target resolution,
        not by direct sentence matching but by comparing the **nature** of the resolution strategy itself.
        You must express the similarity as a percentage, rounded to one decimal place.""",
        verbose=False,
        allow_delegation=False,
    )

    Analyst_conflict = Agent(
        role="Senior Sentence Sentiment Analyst_conflict",
        goal=f"Determine how similar the child's proposed resolution method is to '{Analyse_conflict}' and express the similarity as a percentage (rounded to one decimal place).",
        backstory="""You are an analyst who observes specific conflict situations and evaluates the resolution methods provided by children.
        Your role is to check if you have answered the right questions.
        The order may be changed, but in the case of an answer that deviates from the existing answer, a name that does not exist may be mentioned or a name that should be mentioned is omitted, and the wrong answer may be processed.""",
        verbose=False,
        allow_delegation=False,)

    Analyst_cause = Agent(
        role="Senior Sentence Sentiment Analyst_cause",
        goal=f"Check the following answers and '{Analyse_cause}', determine whether they are correct or not and mark Yes or No.",
        backstory="""You are an analyst who observes specific conflict situations and evaluates the resolution methods provided by children.
        Your role is to check if you have answered the right questions.
        The order may be changed, but in the case of an answer that deviates from the existing answer, a name that does not exist may be mentioned or a name that should be mentioned is omitted, and the wrong answer may be processed.""",
        verbose=False,
        allow_delegation=False,)
    
    Analyst_subject = Agent(
        role="Senior Sentence Sentiment Analyst_subject",
        goal=f"Check the following answers and '{Analyse_subject}', determine whether they are correct or not and mark Yes or No.",
        backstory="""You are an analyst who observes specific conflict situations and evaluates the resolution methods provided by children.
        Your role is to check if you have answered the right questions.
        Minor content may be wrong, but if the content deviates too much, the wrong answer should be processed.""",
        verbose=False,
        allow_delegation=False,)
    
    Recorder = Agent(
        role="Analysis Recorder",
        goal="Compile and present the similarity results from all analysts.",
        backstory="""You are responsible for collecting and summarizing the similarity percentage results.
        Your task is to present a structured summary without additional explanations.""",
        verbose=False,
        allow_delegation=False,
    )



    # 작업 정의
    Analyze_A = Task(
    description=f"""
    **Task:**  
    Analyze the provided resolution method:  
    '**{child_response}**'

    Compare it to the target resolution strategy:  
    '**{Analyse_standard_A}**'

    Also consider: among the four strategies below (A, B, C, D), evaluate whether this response is **most closely aligned with strategy A**.

    - A: "{Analyse_standard_A}"
    - B: "{Analyse_standard_B}" 
    - C: "{Analyse_standard_C}"
    - D: "{Analyse_standard_D}."

    **Evaluation Criteria:** 
    - **Very High Similarity (80-100%)**: The response strongly confronts the person, insisting on correcting their behavior even if it leads to conflict.  
    - **High Similarity (60-79%)**: The response directly addresses the issue and confronts the person but considers negotiation or compromise.  
    - **Moderate Similarity (40-59%)**: The response points out the issue but leans more towards persuasion rather than direct confrontation.  
    - **Low Similarity (20-39%)**: The response mentions the issue but prefers alternative resolution methods over confrontation.  
    - **Very Low Similarity (0-19%)**: The response avoids confronting the issue directly and strongly prefers to avoid conflict.  

    **Format:**  
Provide a single numerical value as a percentage (%), measured precisely.
The output MUST be in the format: XX.X%.
Do NOT include explanations, analysis, or any additional text.
The value must be within the range of 5.0 to 95.9.
    """,
    agent=Analyst_A,
    expected_output="XX.X"
)

    Analyze_B = Task(
    description=f"""
    **Task:**  
    Analyze the provided resolution method:  
    '**{child_response}**'

    Compare it to the target resolution strategy:  
    '**{Analyse_standard_B}**'

    Also consider: among the four strategies below (A, B, C, D), evaluate whether this response is **most closely aligned with strategy B**.

    - A: "{Analyse_standard_A}"
    - B: "{Analyse_standard_B}" 
    - C: "{Analyse_standard_C}"
    - D: "{Analyse_standard_D}."

    **Evaluation Criteria:**  
    - **Very High Similarity (80-100%)**: The response completely ignores the issue and makes no attempt to address it.  
    - **High Similarity (60-79%)**: The response acknowledges the issue but does not take any meaningful action to resolve it.  
    - **Moderate Similarity (40-59%)**: The response mentions the issue but does not actively try to solve it, remaining passive.  
    - **Low Similarity (20-39%)**: The response shows some willingness to address the problem but hesitates to take action.  
    - **Very Low Similarity (0-19%)**: The response actively tries to resolve the issue, showing little to no inclination to ignore it.  

    **Format:**  
Provide a single numerical value as a percentage (%), measured precisely.
The output MUST be in the format: XX.X%.
Do NOT include explanations, analysis, or any additional text.
The value must be within the range of 5.0 to 95.9.
    """,
    agent=Analyst_B,
    expected_output="XX.X"
)

    Analyze_C = Task(
    description=f"""
    **Task:**  
    Analyze the provided resolution method:  
    '**{child_response}**'

    Compare it to the target resolution strategy:  
    '**{Analyse_standard_C}**'

    Also consider: among the four strategies below (A, B, C, D), evaluate whether this response is **most closely aligned with strategy C**.

    - A: "{Analyse_standard_A}"
    - B: "{Analyse_standard_B}" 
    - C: "{Analyse_standard_C}"
    - D: "{Analyse_standard_D}."

    **Evaluation Criteria:**  
    - **Very High Similarity (80-100%)**: The response fully takes over the task without involving the uncooperative member.  
    - **High Similarity (60-79%)**: The response mostly takes on the task but leaves some room for possible involvement of the other person.  
    - **Moderate Similarity (40-59%)**: The response involves doing part of the task while attempting to engage the uncooperative member.  
    - **Low Similarity (20-39%)**: The response prefers to persuade the person rather than taking over the work.  
    - **Very Low Similarity (0-19%)**: The response strongly encourages the person to participate and avoids doing the task alone.  

    **Format:**  
    Provide a single numerical value as a percentage (%), measured precisely.
    The output MUST be in the format: XX.X%.
    Do NOT include explanations, analysis, or any additional text.
    The value must be within the range of 5.0 to 95.9.
    """,
    agent=Analyst_C,
    expected_output="XX.X"
)

    Analyze_D = Task(
    description=f"""
    **Task:**  
    Analyze the provided resolution method:  
    '**{child_response}**'

    Compare it to the target resolution strategy:  
    '**{Analyse_standard_D}**'

    Also consider: among the four strategies below (A, B, C, D), evaluate whether this response is **most closely aligned with strategy D**.

    - A: "{Analyse_standard_A}"
    - B: "{Analyse_standard_B}" 
    - C: "{Analyse_standard_C}"
    - D: "{Analyse_standard_D}."

    **Evaluation Criteria:**  
    - **Very High Similarity (80-100%)**: The response focuses strongly on persuasion and encourages cooperation without conflict.  
    - **High Similarity (60-79%)**: The response primarily uses persuasion but also considers alternative approaches such as indirect confrontation or compromise.  
    - **Moderate Similarity (40-59%)**: The response attempts persuasion but also includes avoidance or other mixed strategies.  
    - **Low Similarity (20-39%)**: The response includes some persuasion elements, but the main approach relies on other strategies (e.g., ignoring, confronting, or taking over tasks).  
    - **Very Low Similarity (0-19%)**: The response does not involve persuasion and follows a completely different resolution approach.  

    **Format:**  
    Provide a single numerical value as a percentage (%), measured precisely.
    The output MUST be in the format: XX.X%.
    Do NOT include explanations, analysis, or any additional text.
    The value must be within the range of 5.0 to 95.9.
    """,
    agent=Analyst_D,
    expected_output="XX.X"
    )

    Analyze_conflict = Task(
        description=f"""
        **Task:**  
        Analyze the provided resolution method:  
        '**{conflict_response}**'

        Compare it to the target resolution strategy:  
        '**{Analyse_conflict}**'


        """,
        agent=Recorder,
        context=[Analyze_A,Analyze_B,Analyze_C,Analyze_D],
        expected_output=bool
    )

    Analyze_cause = Task(
        description=f"""
        **Task:**  
        Analyze the provided resolution method:  
        '**{cause_response}**'

        Compare it to the target resolution strategy:  
        '**{Analyse_cause}**'
        """,
        agent=Recorder,
        context=[Analyze_A,Analyze_B,Analyze_C,Analyze_D],
        expected_output=bool
    )

    Analyze_subject = Task(
        description=f"""
       **Task:**  
        Analyze the provided resolution method:  
        '**{subject_response}**'

        Compare it to the target resolution strategy:  
        '**{Analyse_subject}**'
        """,
        agent=Recorder,
        context=[Analyze_A,Analyze_B,Analyze_C,Analyze_D],
        expected_output=bool
    )

    Record_Task = Task(
        description=f"""
        Collect and present the similarity scores from all analysts.  
        Format the results as a structured list:  
        ```
        [A: XX.X%, B: XX.X%, C: XX.X%, D: XX.X%, S: XX.X%]
        ```
        Ensure there are **no additional comments** or explanations.
        """,
        agent=Recorder,
        context=[Analyze_A,Analyze_B,Analyze_C,Analyze_D],
        expected_output="[A: XX.X%, B: XX.X%, C: XX.X%, D: XX.X%, S: XX.X%]"
    )



    crew = Crew(
        agents=[Analyst_A, Analyst_B, Analyst_C, Analyst_D, Recorder],
        tasks=[Analyze_A, Analyze_B, Analyze_C, Analyze_D, Record_Task],
        verbose=False
    )

    result = crew.kickoff()

    # 수정된 출력 추출 방식
    output = str(result).strip()
    print("Result:", output)

    # 정규식 파싱
    match = re.match(r"\[A:\s*([\d.]+)%,\s*B:\s*([\d.]+)%,\s*C:\s*([\d.]+)%,\s*D:\s*([\d.]+)%,\s*S:\s*([\d.]+)%\]",output)
    if match:
        scores["A"].append(float(match.group(1)))
        scores["B"].append(float(match.group(2)))
        scores["C"].append(float(match.group(3)))
        scores["D"].append(float(match.group(4)))
        scores["S"].append(float(match.group(5)))
    else:
        print("Failed to parse:", output)


    end = time.time()
    print(f"Time: {end - start:.1f} seconds")

# 평균 계산
average_scores = {
    k: round(statistics.mean(v), 1) if v else 0.0 for k, v in scores.items()
}

ansA_weight=[0.33, 0.28, 0.11, 0.05, -0.61]
ansB_weight=[0.06, -0.01, 0.11, -0.05, 0.75]
ansC_weight=[0.08, 0.43, 0.16, 0.00, 0.14]
ansD_weight=[-0.28, 0.52, 0.01, 0.03, -0.12]

#성향 1 가중치: A:33 B:6 C:8 D:-28
social_result["So1"] = round(((average_scores["A"]*ansA_weight[0])+(average_scores["B"]*ansB_weight[0])+(average_scores["C"]*ansC_weight[0])+(average_scores["D"]*ansD_weight[0]))/4,2)

#성향 2 가중치: A:28 B:-1 C:43 D:52
social_result["So2"] = round(((average_scores["A"]*ansA_weight[1])+(average_scores["B"]*ansB_weight[1])+(average_scores["C"]*ansC_weight[1])+(average_scores["D"]*ansD_weight[1]))/4,2)

#성향 3 가중치: A:11 B:11 C:16 D:1 
social_result["So3"] = round(((average_scores["A"]*ansA_weight[2])+(average_scores["B"]*ansB_weight[2])+(average_scores["C"]*ansC_weight[2])+(average_scores["D"]*ansD_weight[2]))/4,2)

#성향 4 가중치: A:5 B:-5 C:0 D:3
social_result["So4"] = round(((average_scores["A"]*ansA_weight[3])+(average_scores["B"]*ansB_weight[3])+(average_scores["C"]*ansC_weight[3])+(average_scores["D"]*ansD_weight[3]))/4,2)

#성향 5 가중치: A:-61 B:75 C:14 D:-12
social_result["So5"] = round(((average_scores["A"]*ansA_weight[4])+(average_scores["B"]*ansB_weight[4])+(average_scores["C"]*ansC_weight[4])+(average_scores["D"]*ansD_weight[4]))/4,2)

# 최종 출력
print("\nFinal Average Similarity Scores:")
print(f"[A: {average_scores['A']}%, B: {average_scores['B']}%, C: {average_scores['C']}%, D: {average_scores['D']}%, S: {average_scores['S']}%]")
print("\nFinal Social Weighting Scores:")
print(f"[So1_altruism: {social_result['So1']}%, So2_initiative: {social_result['So2']}%, So3_self-assertion: {social_result['So3']}%, So4_self-restraint: {social_result['So4']}%, So5_Empathy: {social_result['So5']}%]")

output_data = {
    "prompt": prompt_text.strip(),
    "child_response": child_response,
    "situation_response": "situation_response",
    "average_scores": {
        "A": average_scores["A"],
        "B": average_scores["B"],
        "C": average_scores["C"],
        "D": average_scores["D"],
        "S": average_scores["S"]
    },
    "social result": {
        "So1":social_result["So1"],
        "So2":social_result["So2"],
        "So3":social_result["So3"],
        "So4":social_result["So4"],
        "So5":social_result["So5"]
    }
}


# 파일로 저장
with open("child_conflict_analysis_result.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print("\n결과가 'child_conflict_analysis_result.json' 파일에 저장되었습니다.")


#아동 해결 방식
# I will tell them that they have to help because it's not fair if only some of us do all the work. If they don’t listen, I will keep telling them until they do, even if they get mad at me.A 우선
# I don’t want to start a fight, so I will just do my own part and not worry about them. If they don’t help, it’s their choice, not mine.B우선
# If they don’t want to help, I will just do their part so we can finish quickly. I don’t want to argue about it. C우선
# I will ask them nicely to help and explain that we all need to work together. If they still don’t want to help, I will ask the group leader to talk to them instead. D 우선
# First, I will talk to them nicely and ask if they can do something small. If they still don’t help, I will do a little more myself but also tell the teacher so it’s fair for everyone. 밸런스형
# I will make a fun game out of the research and see if they join in. If they still don’t, I will just work with the others and not worry too much. 창의적 방법

#아동 상황 분석
#One group member is not helping at all, and that makes it unfair for the rest of us who are trying hard. If we try to talk to them, they might get angry, so it’s hard to decide what to do. Everyone is feeling upset, and it could cause problems in the group. 100~80%
#One friend is not helping, and it’s making the others angry. It might start a fight if we talk to them, so it’s better to be careful. 60%~80%
#One person is not doing their part. It’s not fair, but maybe it’s okay if the others finish the work. 40%~20%
#Someone in the group is not doing anything. I don’t really care though. 20%
#I like Japan. I want to write about sushi."10%


