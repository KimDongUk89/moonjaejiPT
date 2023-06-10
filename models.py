from flask import request, redirect, jsonify, session, url_for, make_response
from app import db
from api import gpt
import os
from FileReader import readFile
from URLReader import readURL
import uuid

# 유저 관련 클래스
class User():
    def registerUser(self):
        
        # 로그인 정보를 db에 저장하는데, 이미 등록된 id라면 이름이나 프로필 사진이 바꼈는지 확인하고 업데이트, 처음 등록이라면 insert
        data = {
            "_id" : uuid.uuid4().hex,
            "id" : request.form.get('email'),
            "name" : request.form.get('name'),
            "profile_image_url" : request.form.get('profile_image_url'),
            "thumbnail_image_url" : request.form.get('thumbnail_image_url'),
            "platform" : request.form.get('platform'),
            "access_token" : request.form.get('access_token')
        }

        filter_query = {"id":data["id"], "platform":data["platform"]}
        update_data = {"$set" : {"name" : data["name"], "profile_image_url" : data["profile_image_url"], "thumbnail_image_url" : data["thumbnail_image_url"], "access_token" : data['access_token']}}

        result = db.user.update_one(filter_query, update_data)

        # 쿠키 생성을 위함.
        resp = make_response()
        
        # db에 저장되어 있는 사용자가 없다면 등록
        if result.matched_count == 0:
            db.user.insert_one(data)
            resp.set_cookie('user_id',data['_id']) # 현재 접속한 유저의 고유 아이디를 쿠키에 저장.
            
            return 'data inseted'
        # 이미 있다면 업데이트한거
        else:
            user_id = db.user.find_one({"id":data["id"], "platform":data["platform"]})['_id']
            resp.set_cookie('user_id',user_id)
            
            return 'data updated'

    def getUserdata(user_id):
        # 현재 로그인한 사용자 정보
        user_data = db.user.find_one({"_id": user_id})
        
        # 현재 로그인한 계정이 생성한 문제 가져오기.
        datas = db.summaries.find({"owner" : user_id})

        doc_list = []
        for doc in datas:
            data = {
                "title" : doc['title'],
            }
            doc_list.append(data)

        result = {
            'user_data' : user_data,
            'data' : doc_list
        }
        return jsonify(result)

# 문서 관련 클래스
class Doc():
    def show(document_id):
        summary = db.summaries.find_one({"_id" : document_id})
        questions = db.questions.find({"doc_id" : document_id})
        questions_count = db.questions.count_documents({'doc_id' : document_id})

        data_list = []
        # 각 문제에 대해 package 구성(문제 아이디 + 문제 + 정답 + 해설 + 사용자 입력 값 + 메모)
        for question in questions:
            question_id = question.get('_id')

            answer = db.answers.find_one({"question_id":question_id})
            explanation = db.explanations.find_one({"question_id":question_id})

            data = {
                'question_id' : question_id,
                'question' : question['question'],
                'answer' : answer['answer'],
                'explanation' : explanation['explanation'],
                'user_select' : answer['user_select'],
                'memo' : question['memo']
            }
            data_list.append(data)

        response = {
            'summary' : summary['summary'], # 요약본 내용
            'condition' : summary['condition'], # 문서가 채점상태인지 아닌지 ("scored","unscored")
            'data' : data_list, # 위에서 만든 packages
            'data_num' : questions_count # 전체 문제 개수
        }
    
        return jsonify(response)


    def createDoc(self,user):
        # 문제 유형 입력받기
        types=[]
        for i in request.form:
            if i in ['multiple choice', 'single term answer', 'fill-in-the-blank', 'true or false']:
                types.append(i.upper())

        # 텍스트로 직접 입력한거 읽기
        if request.form['doc']:
            text = request.form['doc']

        # 파일 입력한다면
        if request.files['file']:
            text = readFile()
        
        # URL 입력한다면
        if request.form.get('url'):
            text = readURL()

        # 입력된 내용을 가지고 ChatGPT에 문제 생성 요청
        result = gpt(text,user,types)
        return result
        # # 현재 문서 아이디(이걸로 문제 출제 완료 후 바로 만들어진 문제 페이지로 이동)
        # now_doc_id = session.get('now_doc_id')
        # target_url = url_for('show', document_id = now_doc_id)
        # return redirect(target_url)

    # 문서 삭제
    def delete(document_id):

        result = db.summaries.find_one({'_id' : document_id})
        if result.matched_count == 0:
            return "Fail"
        else:
            db.summaries.delete_one({'_id' : document_id})
        
        result = db.questions.find({'doc_id' : document_id})
        if result.matched_count == 0:
            return "Fail"
        else:
            db.questions.delete_many({'doc_id' : document_id})

        result = db.answers.find({'doc_id' : document_id})
        if result.matched_count == 0:
            return "Fail"
        else:
            db.answers.delete_many({'doc_id' : document_id})
        
        result = db.explanations.find({'doc_id' : document_id})
        if result.matched_count == 0:
            return "Fail"
        else:
            db.explanations.delete_many({'doc_id' : document_id})
        
        return "Success"

    # 문제 채점
    def score(user_select):
        
        # 문서 아이디 가져오기
        document_id = db.questions.find_one({'_id':user_select[0]['question_id']})['doc_id']
        # 문서 상태를 채점된 상태로 바꾸기
        db.summaries.update_one({'_id':document_id}, {"$set":{"condition":"scored"}})

        # 모든 문제에 대한 사용자 답 채점
        for package in user_select:
            # 사용자가 입력한 값
            user_answer = package['user_select']
            # 사용자가 입력한 값 db에 저장
            db.answers.update_one({'question_id' : package['question_id']}, {"$set":{"user_select":user_answer}})
            
            # 정답 가져오기
            answer = db.answers.find_one({'question_id' : package['question_id']})['answer']
            
            # 정답
            if answer.strip() == user_answer.strip():
                update_data = {"$set" : {"condition" : "right"}}
                db.questions.update_one({'_id':package['question_id']}, update_data)
            #오답
            else:
                update_data = {"$set" : {"condition" : "wrong"}}
                db.questions.update_one({'_id':package['question_id']}, update_data)

        # 회차에 따른 점수 업데이트
        types = ['MULTIPLE CHOICE', 'SINGLE TERM ANSWER', 'FILL-IN-THE-BLANK', 'TRUE OR FALSE']
        data_list = []
        for type in types:
            percent = round(db.questions.count_documents({'doc_id':document_id, 'type':type, 'condition':'right'}) / db.questions.count_documents({'doc_id':document_id, 'type':type}) * 100)
            data = {
                type : percent
            }
            data_list.append(data)
    
        db.summaries.update_one({"_id":document_id},{"$push":{"score":data_list}})
        round_num = len(db.summaries.find_one({'_id':document_id})['score']) # 채점 횟수
        
        # 채점횟수와 채점 결과 return
        result = {
            "round" : round_num,
            "scores" : data_list
        }
        return result

    # 리셋
    def reset(document_id):
        # 문제 채점 상태 초기화
        db.questions.update_many({'doc_id':document_id},{"$set":{"condition" : "normal"}})
        # 사용자가 입력했던 값 초기화
        db.answers.update_many({'doc_id':document_id}, {"$set":{"user_select":""}})
        # 문서 채점 상태 초기화
        db.summaries.update_one({'_id':document_id}, {"$set":{"condition":"unscored"}})
        return "Reset Success"

    # 유저가 중간에 나갔을 때 입력하던 값 저장
    def save(document_id, user_select):
        # 사용자가 입력한 값 저장
        db.questions.update_many({'question_id':user_select['question_id']}, {'$set':{"user_select":user_select['user_select']}})
        return "Save Success"