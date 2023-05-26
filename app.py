from flask import Flask, render_template, request, session, jsonify
import pymongo

from config import CLIENT_ID, REDIRECT_URL

app = Flask (__name__) 
app.secret_key=b'\x8e\\\x99\xe8\x14\xd4\xb5\xa8\xa2\xfb\x160.\xc8+\xf2'

# mongodb 연결
client = pymongo.MongoClient('localhost', 27017)
db = client.question_pt

# circular import 문제로 여기서 import
from models import User, Doc

@app.route('/') 
def index(): 
    return render_template('index.html')

@app.route('/user_register', methods=['POST'])
def user_register():
    return User().user_register()

@app.route('/main/', methods=['GET','POST'])
def home():
    # 현재 로그인한 계정이 생성한 문제 가져오기.
    data = db.summaries.find({"owner" : session.get('now_user_email')})
    
    return render_template('main.html', data=data)

# 문제 생성 페이지
@app.route('/create/')
def create():
    return render_template('create.html')

# 문서 처리 페이지
@app.route('/doc/', methods=['POST'])
def document():
    return Doc().doc(user=session.get('now_user_email'))

# 요약, 문제 출제 페이지
@app.route('/doc_summary/<document_id>', methods=['GET','POST'])
def print_summary(document_id):
    
    summary = db.summaries.find({"_id" : document_id})[0]['summary']
    questions = db.questions.find({"doc_id" : document_id})[0]['question']
    answers = db.answers.find({"doc_id" : document_id})[0]['answer']
    return render_template('doc_summary.html', summary=summary, questions=questions, answers=answers)