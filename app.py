from crypt import methods
from operator import methodcaller
from urllib import response
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

# 로그인한 후 로그인한 계정이 db에 있는지 확인
@app.route('/registerUser', methods=['POST'])
def registerUser():
    return User().registerUser()


# 테스트용 html
@app.route('/main/', methods=['GET','POST'])
def home():
    # 현재 로그인한 사용자 정보
    user_data = db.user.find_one({"_id": session.get('now_user_id')})
    
    # 현재 로그인한 계정이 생성한 문제 가져오기.
    data = db.summaries.find({"owner" : session.get('now_user_id')})
    
    return render_template('main.html', user_data=user_data,data=data)


# 사용자 프로필이나 사이드바에 올릴 생성된 문서 목록들을 위함.
@app.route('/getUserdata', methods=['GET'])
def getUserdata():
    user_id = request.cookies.get('user_id')
    return User.getUserdata(user_id)

# 문제 생성 페이지(테스트용)
@app.route('/create/')
def create():
    return render_template('create.html')

# 문서 처리 페이지
@app.route('/createDoc/', methods=['POST'])
def document():
    return Doc().createDoc(user=request.cookies.get('user_id'))

# 요약, 문제 출제 페이지
@app.route('/show/<document_id>', methods=['GET'])
def show(document_id):
    return Doc.show(document_id=document_id)

# 문서 삭제
@app.route('/delete/<document_id>', methods=['GET'])
def delete(document_id):
    return Doc.delete(document_id = document_id)

# 채점
@app.route('/score', methods=['POST'])
def score():
    user_select = request.get_json()
    return Doc.score(user_select["packages"])

# 리셋
@app.route('/reset/<document_id>', methods=['GET'])
def reset(document_id):
    return Doc.reset(document_id)

# 사용자 입력 값 저장
@app.route('/save', methods=['POST'])
def save():
    user_select = request.get_json()
    return Doc.save(user_select)