import openai
from app import db
import uuid
import time
import re

# openai api key
openai.api_key = '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'


def gpt(text,user,types):
    start = time.time()

    # 요약본 만들기
    messages = [{
        'role': 'system',
        'content': 'You are a helpful assistant for summarizing books.'
    }, {
        'role': 'user',
        'content': f'Summarize this in Korean : {text}'
    }]

    res = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages
    )

    summary_msg = res['choices'][0]['message']['content']

    # 요약본(고유 아이디, 생성 주인, 요약본 내용, 문서 제목, 채점 점수, 채점 상태)    
    summary = {
        "_id":uuid.uuid4().hex, 
        "owner":user,
        "summary":summary_msg,
        "title":summary_msg[:20],
        "score": [],
        "condition":"unscored"
    }
    
    # 하나의 문서에 하나의 요약본만 존재하므로 요약본의 id를 now_doc_id로 정함.
    db.summaries.insert_one(summary) # db에 입력
    

    # 각 유형마다의 최소 문제 개수
    question_num = 3

    # 각 문제유형마다 chatGPT한테 문제유형에 맞는 문제 생성 요청
    # types : ['MULTIPLE CHOICE', 'SINGLE TERM ANSWER', 'FILL-IN-THE-BLANK', 'TRUE OR FALSE']
    for question_type in types:
    
        if question_type == 'MULTIPLE CHOICE':
            messages = [{
                'role': 'system',
                'content': 'You are an assistant who helps make test questions.'
            }, {
                'role': 'user',
                'content': f'I want to make questions and corresponding answers, explanations prepare for the test.  \
                question types: {question_type}. text: {text}. \
                \
                Here are format guides. \
                \
                Read given text and give {question_type} questions that will appear on the exam. \
                The number of multiple choice questions is four. \
                DO NOT MISS EVEN ONE THING.  \
                Do not specify question type on the beginning.   \
                Please wrie answers in a concise manner. \
                \
                Here are detail examples of each types \
                Example of multiple choice\
                문제1: 인텔 관리 엔진은 운영 체제와 어디에 있나? \
                a) 운영 체제보다 상위에 위치해 있어 운영 체제와 연관성이 높음. \
                b) 운영 체제 하부에 위치해 운영 체제에서 건드릴 수 없음. \
                c) 독자적인 운영체제로 구동되며 운영체제와 큰 연관이 없음. \
                d) 사용자가 결정할 수 있는 영역으로 운영 체제와 상호작용 함. \
                답: b \
                해설: 인텔 관리 엔진은 운영 체제보다 하부에 위치해 운영 체제에서 건드릴 수 없습니다. \
                \
                문제2: 무선 인터넷 공유기/AP에 연결되는 장치가 많아지면 무슨 문제가 있을까요?    \
                a) 연결 장치가 많아지면 전송 속도가 더 빨라집니다.  \
                b) 연결 장치가 많아지면 전송 속도는 반비례하여 감소합니다.  \
                c) 연결 장치 수와 전송 속도는 무관합니다.  \
                d) 연결 장치 수에 상관없이 전송 속도는 일정합니다.  \
                답: b   \
                해설: 무선 인터넷 공유기/AP에 연결되는 장치가 많아질수록 전송 속도는 반비례하여 감소합니다. 최대 연결 가능한 장치 수는 11개 이상부터는 본격적으로 버벅거림을 느낄 수 있다고 합니다. \
                \
                Follow the format guide and examples. The example is just an EXAMPLE. Just refer to it and DO NOT copy it.  \
                Please write MORE than {question_num} QUESTIONS, ANSWERS and EXPLANATIONS in the format. Write in KOREAN. \
                Look at the examples and give questions, answers, and explanations in the FIXED FORMAT.  \
                Please follow examples that i showed you!   \
                CONTINUE until everything is printed out. step by step.  \
                Im planning to save this into the database by distinguishing each as "문제", "답", and "해설". Therefore, please provide each output separately.\
                '
            }]
        elif question_type == 'SINGLE TERM ANSWER':
            messages = [{
                'role': 'system',
                'content': 'You are an assistant who helps make test questions.'
            },{
                'role': 'user',
                'content': f'I want to make questions and corresponding answers, explanations prepare for the test.  \
                I want all type of questions in {question_type}. \
                \
                question types: {question_type}. text: {text}. \
                \
                Here are format guides. \
                Read given text and give {question_type} questions that will appear on the exam. \
                The number of multiple choice questions is four. \
                Give me ALL TYPE OF {question_type} questions. DO NOT MISS EVEN ONE THING.  \
                Do not specify question type on the beginning.   \
                Please wrie answers in a concise manner. \
                \
                Here are detail examples of each types \
                Example of single term answer\
                문제3: 윈도우 커널의 프로그램 이름은? \
                답: ntoskrnl.exe \
                해설: 윈도우 커널의 프로그램 이름은 ntoskrnl.exe입니다.\
                \
                문제2: 802.11r(Fast Roaming)이란 무엇인가?  \
                답: 이동 중에도 Wi-Fi를 사용할 수 있는 방식 \
                해설: 802.11r(Fast Roaming)은 이동 중에도 Wi-Fi를 사용할 수 있는 방식으로, SSID가 같고 제일 신호가 센 AP를 자동으로 연결하여 인터넷이 끊기지 않게 합니다.   \
                \
                Follow the format guide and examples. The example is just an EXAMPLE. Just refer to it and DO NOT copy it.  \
                Please write MORE than {question_num} QUESTIONS, ANSWERS and EXPLANATIONS in the format. Write in KOREAN. \
                Look at the examples and give questions, answers, and explanations in the FIXED FORMAT.  \
                Please follow examples that i showed you!   \
                CONTINUE until everything is printed out. step by step.  \
                Im planning to save this into the database by distinguishing each as "문제", "답", and "해설". Therefore, please provide each output separately.\
                '
            }]
        elif question_type == 'FILL-IN-THE-BLANK':
            messages = [{
                'role': 'system',
                'content': 'You are an assistant who helps make test questions.'
            }, {
                'role': 'user',
                'content': f'I want to make questions and corresponding answers, explanations prepare for the test.  \
                I want all type of questions in {question_type}. \
                \
                question types: {question_type}. text: {text}. \
                \
                Here are format guides. \
                Read given text and give {question_type} questions that will appear on the exam. \
                The number of multiple choice questions is four. \
                Give me ALL TYPE OF {question_type} questions. DO NOT MISS EVEN ONE THING.  \
                Do not specify question type on the beginning.   \
                Please wrie answers in a concise manner. \
                \
                Here are detail examples of each types \
                Examples of fill-in-the-blank \
                문제1: 윈도우에서 가장 많이 사용되는 프로그램은 ____ 이다. \
                답: Shell \
                해설: 윈도우에서 가장 많이 사용되는 프로그램은 Shell입니다. \
                \
                문제2: 근거리 통신을 전제로 제정된 규약이기 때문에 커버리지가 _____ 정도다. \
                답: 개활지에서 200m \
                해설: Wireless LAN은 근거리 통신을 전제로 제정된 규약이기 때문에 커버리지가 개활지에서 200m 정도입니다. \
                \
                Follow the format guide and examples. The example is just an EXAMPLE. Just refer to it and DO NOT copy it.  \
                Please write MORE than {question_num} QUESTIONS, ANSWERS and EXPLANATIONS in the format. Write in KOREAN. \
                Look at the examples and give questions, answers, and explanations in the FIXED FORMAT.  \
                Please follow examples that i showed you!   \
                CONTINUE until everything is printed out. step by step.  \
                Im planning to save this into the database by distinguishing each as "문제", "답", and "해설". Therefore, please provide each output separately.\
                '
            }]
        elif question_type == 'TRUE OR FALSE':
            messages = [{
                'role': 'system',
                'content': 'You are an assistant who helps make test questions.'
            }, {
                'role': 'user',
                'content': f'I want to make questions and corresponding answers, explanations prepare for the test.  \
                I want all type of questions in {question_type}. \
                \
                question types: {question_type}. text: {text}. \
                \
                Here are format guides. \
                Read given text and give {question_type} questions that will appear on the exam. \
                The number of multiple choice questions is four. \
                Give me ALL TYPE OF {question_type} questions. DO NOT MISS EVEN ONE THING.  \
                Do not specify question type on the beginning.   \
                Please wrie answers in a concise manner. \
                \
                Here are detail examples of each types \
                Examples of true of false \
                문제1: 인텔 관리 엔진은 운영 체제의 일부이기 때문에 윈도우에서 사용할 수 없다. \
                답: 거짓 \
                해설: 인텔 관리 엔진은 윈도우에서도 사용할 수 있습니다. \
                \
                문제2: 802.11r(Fast Roaming)은 이동 중에도 Wi-Fi를 사용할 수 있다.  \
                답: 참  \
                해설: 802.11r(Fast Roaming)은 이동 중에도 Wi-Fi를 사용할 수 있도록 해주는 규격입니다.   \
                \
                Follow the format guide and examples. The example is just an EXAMPLE. Just refer to it and DO NOT copy it.  \
                Please write MORE than {question_num} QUESTIONS, ANSWERS and EXPLANATIONS in the format. Write in KOREAN. \
                Look at the examples and give questions, answers, and explanations in the FIXED FORMAT.  \
                Please follow examples that i showed you!   \
                CONTINUE until everything is printed out. step by step.  \
                Im planning to save this into the database by distinguishing each as "문제", "답", and "해설". Therefore, please provide each output separately.\
                '
            }]

        res = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages
        )
        return_data = res['choices'][0]['message']['content']

        # 데이터를 파싱하기 위한 정규표현식
        question_pattern = re.compile(r'(문제 ?\d+:|^\d+\.\s)([\s\S]*?)(?=답:|정답:)', re.M)
        answer_pattern = re.compile(r'(답:|정답:)([\s\S]*?)(?=해설)', re.M)
        explanation_pattern = re.compile(r'해설:([\s\S]*?)(?=문제 ?\d+|$)', re.M)

        # 각 카테고리에 대해 데이터를 분류
        questions = [question[1].strip() for question in re.findall(question_pattern, return_data)]
        answers = [answer[1].strip() for answer in re.findall(answer_pattern, return_data)]
        explanations = [explanation.strip() for explanation in re.findall(explanation_pattern, return_data)]


        for idx in range(len(questions)):
            # 문제(고유 아이디, 문서 아이디, 생성 주인, 문제 내용, 문제 유형, 정답/오답 유무, 메모)
            question = {
                "_id":uuid.uuid4().hex,
                "doc_id":summary['_id'],
                "owner":user,
                "question":questions[idx],
                "type":question_type,
                "condition":"normal",
                'memo':''
            }
            # 답(고유 아이디, 문서 아이디, 문제 아이디, 생성 주인, 답 내용, )
            answer={
                "_id":uuid.uuid4().hex,
                "doc_id":summary['_id'],
                "question_id":question['_id'],
                "owner":user,
                "answer":answers[idx],
                "user_select" : ""
            }
            # 해설(고유 아이디, 문서 아이디, 생성 주인, 해설)
            explanation={
                "_id":uuid.uuid4().hex,
                "doc_id":summary['_id'],
                "question_id":question['_id'],
                "owner":user,
                "explanation":explanations[idx],
            }
            db.explanations.insert_one(explanation) # db에 입력
            db.questions.insert_one(question) # db에 입력
            db.answers.insert_one(answer) # db에 입력

    end=time.time()
    print(f"문서 만드는 데 {end-start:.2f}초 걸린다")

    return summary['_id']