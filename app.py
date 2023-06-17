from flask import Flask, render_template, request
import pymongo
from flask_cors import CORS

from config import CLIENT_ID, REDIRECT_URL

app = Flask (__name__) 
app.secret_key=b'\x8e\\\x99\xe8\x14\xd4\xb5\xa8\xa2\xfb\x160.\xc8+\xf2'
CORS(app, support_credentials=True, origins='*')

# mongodb 연결
client = pymongo.MongoClient('localhost', 27017)
db = client.question_pt

@app.route('/') 
def index():
    return render_template('index.html')

# 로그인한 후 로그인한 계정이 db에 있는지 확인
@app.route('/registerUser', methods=['GET', 'POST'])
def registerUser():
    from models import User, Doc

    return User().registerUser()


# 테스트용 html
@app.route('/main/', methods=['GET','POST'])
def home():
    user_id = request.cookies.get('user_id')

    # 현재 로그인한 사용자 정보
    user_data = db.user.find_one({"_id": user_id})
    
    # 현재 로그인한 계정이 생성한 문제 가져오기.
    data = db.summaries.find({"owner" : user_id})
    
    return render_template('main.html', user_data=user_data,data=data)


# 사용자 프로필이나 사이드바에 올릴 생성된 문서 목록들을 위함.
@app.route('/getUserdata', methods=['GET'])
def getUserdata():
    from models import User, Doc

    user_id = request.cookies.get('user_id')
    return User.getUserdata(user_id)

# 문제 생성 페이지(테스트용)
@app.route('/create/')
def create():
    return render_template('create.html')

# 문서 처리 페이지
@app.route('/createDoc', methods=['POST'])
def document():
    from models import User, Doc

    return Doc().createDoc()

# 요약, 문제 출제 페이지
@app.route('/show/<document_id>', methods=['GET'])
def show(document_id):
    from models import User, Doc

    return Doc.show(document_id=document_id)

# 테스트용.
@app.route('/showDoc/<document_id>', methods=['GET'])
def showDoc(document_id):
    summary = db.summaries.find_one({"_id" : document_id})
    questions = db.questions.find({"doc_id" : document_id})
    answers = db.answers.find({"doc_id" : document_id})
    explanations = db.explanations.find({"doc_id" : document_id})
    questions_count = db.questions.count_documents({'doc_id' : document_id})

    return render_template('show_doc.html', summary=summary, questions=questions, answers=answers, explanations=explanations, questions_count=questions_count)

# 문서 삭제
@app.route('/delete/<document_id>', methods=['GET'])
def delete(document_id):
    from models import User, Doc

    return Doc.delete(document_id = document_id)

# 채점
@app.route('/score', methods=['POST'])
def score():
    from models import User, Doc

    user_select = request.get_json()
    return Doc.score(user_select["packages"])

# 리셋
@app.route('/reset/<document_id>', methods=['GET'])
def reset(document_id):
    from models import User, Doc

    return Doc.reset(document_id)

# 사용자 입력 값 저장
@app.route('/save', methods=['POST'])
def save():
    from models import User, Doc

    user_select = request.get_json()
    return Doc.save(user_select)

if __name__ == '__main__':
   app.run('172.20.10.3', port=5000, debug=True)