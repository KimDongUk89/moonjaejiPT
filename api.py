import openai
from flask import session
from app import db
import uuid
import re

# openai api key
openai.api_key = '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'

def gpt(text,user,types):
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
    
    summary = {
        "_id":uuid.uuid4().hex,
        "owner":user,
        "summary":summary_msg
    }
    
    session['now_doc_id'] = summary['_id']
    db.summaries.insert_one(summary)
    
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

        question = {
            "_id":uuid.uuid4().hex,
            "doc_id":summary['_id'],
            "owner":user,
            "question":question_msg
        }
        db.questions.insert_one(question)
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
        answer={
            "_id":uuid.uuid4().hex,
            "doc_id":summary['_id'],
            "question_id":question['_id'],
            "owner":user,
            "answer":answer_msg
        }

        db.answers.insert_one(answer)
        answer_list.append(answer)

    return 