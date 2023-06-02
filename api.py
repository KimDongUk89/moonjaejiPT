import openai
from flask import session
from app import db
import uuid
import time

# openai api key
openai.api_key = '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'

def gpt(text,user,types):
    start = time.time()
    question_list = []
    answer_list = []
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

    # 요약본(고유 아이디, 생성 주인, 요약본 내용)    
    summary = {
        "_id":uuid.uuid4().hex,
        "owner":user,
        "summary":summary_msg
    }
    
    # 이 session은 문제와 답을 같은 문서에 대해 불러오기 위함.
    # 하나의 문서에 하나의 요약본만 존재하므로 요약본의 id를 now_doc_id로 정함.
    session['now_doc_id'] = summary['_id']
    db.summaries.insert_one(summary) # db에 입력
    
    # 각 문제유형마다 chatGPT한테 문제유형에 맞는 문제 생성 요청
    for question_type in types:
        
        test_list = [{
            'role': 'system',
            'content': 'You are a helpful assistant for making test question.'
        }]

        messages = [{
            'role': 'system',
            'content': 'You are a helpful assistant for making test question.'
        }, {
            'role': 'user',
            'content': f'I want to be able to answer questions that might appear on an exam about the following. Give me {question_type} questions at least a few that will appear on the exam. text : {text}. Please reply to my request in KOREAN'
        }]

        res = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages
        )
        question_msg = res['choices'][0]['message']['content']

        # GPT가 생성한 질문 담기
        test_list.append({
            'role' : "assistant",
            'content' : question_msg
        })

        # 문제(고유 아이디, 문서 아이디, 생성 주인, 문제 내용)
        question = {
            "_id":uuid.uuid4().hex,
            "doc_id":summary['_id'],
            "owner":user,
            "question":question_msg
        }
        db.questions.insert_one(question) # db에 입력
        question_list.append(question)

        test_list.append({
            'role' : 'user',
            'content' : 'Give me the answer about this question. question : {}. just response only the correct answer'.format(question_msg)
        })

        res = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=test_list
        )
        answer_msg = res['choices'][0]['message']['content']

        # 답(고유 아이디, 문서 아이디, 문제 아이디, 생성 주인, 답 내용)
        answer={
            "_id":uuid.uuid4().hex,
            "doc_id":summary['_id'],
            "question_id":question['_id'],
            "owner":user,
            "answer":answer_msg
        }

        db.answers.insert_one(answer) # db에 입력
        answer_list.append(answer)
    end=time.time()
    print(f"{end-start:.5f}sec")
    return 