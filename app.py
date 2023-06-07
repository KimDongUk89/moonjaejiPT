from operator import methodcaller
from flask import Flask, render_template, request, session, jsonify
import pymongo
from flask_cors import CORS

from config import CLIENT_ID, REDIRECT_URL

app = Flask (__name__) 
app.secret_key=b'\x8e\\\x99\xe8\x14\xd4\xb5\xa8\xa2\xfb\x160.\xc8+\xf2'
CORS(app, origins=["http://localhost:3000"])

# mongodb 연결
client = pymongo.MongoClient('localhost', 27017)
db = client.question_pt

# circular import 문제로 여기서 import
from models import User, Doc

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/user_register', methods=['GET','POST'])
def user_register():
    return User().user_register()

@app.route('/main/', methods=['GET','POST'])
def home():
    # 현재 로그인한 사용자 정보
    user_data = db.user.find_one({"_id": session.get('now_user_id')})
    
    # 현재 로그인한 계정이 생성한 문제 가져오기.
    data = db.summaries.find({"owner" : session.get('now_user_id')})
    print(type(data))
    
    return render_template('main.html', user_data=user_data,data=data)

# 문제 생성 페이지
@app.route('/create/')
def create():
    return render_template('create.html')

# 문서 처리 페이지
@app.route('/create_doc/', methods=['POST'])
def document():
    return Doc().create_doc(user=session.get('now_user_id'))

# 요약, 문제 출제 페이지
@app.route('/show_doc/<document_id>', methods=['GET'])
def print_summary(document_id):
    
    summary = db.summaries.find({"_id" : document_id})[0]
    
    questions = db.questions.find({"doc_id" : document_id})
    
    answers = db.answers.find({"doc_id" : document_id})
    explanations = db.explanations.find({"doc_id" : document_id})
    
    questions_count = db.questions.count_documents({'doc_id' : document_id})
    
    return render_template('show_doc.html', summary=summary, questions=questions, answers=answers, explanations=explanations, document_id=document_id, questions_count=questions_count)

# 문서 삭제
@app.route('/doc_delete/<document_id>', methods=['POST'])
def doc_delete(document_id):
    return Doc.doc_delete(document_id = document_id)

# 채점
@app.route('/scoring/<document_id>', methods=['POST'])
def scoring(document_id):
    answers_dict = request.form.to_dict()
    print(answers_dict)
    return Doc.scoring(document_id, answers_dict)

# 리셋
@app.route('/reset/<document_id>', methods=['POST'])
def reset(document_id):
    return Doc.reset(document_id)
