from flask import request, redirect, jsonify, session, url_for
from app import db
from api import gpt
import os
from FileReader import file_read
from URLReader import url_read
import uuid

# 유저 관련 클래스
class User():
    def user_register(self):

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
        
        # db에 저장되어 있는 사용자가 없다면 등록
        if result.matched_count == 0:
            db.user.insert_one(data)
            print("data inserted")
        # 이미 있다면 업데이트한거
        else:
            print("data updated successfully.")
        
        # 현재 로그인한 사용자 고유 id
        session['now_user_id'] = db.user.find_one({"id":data["id"], "platform":data["platform"]})['_id']
        return redirect('/main/')

# 문서 관련 클래스
class Doc():

    def create_doc(self,user):
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
            text = file_read()
        
        # URL 입력한다면
        if request.form.get('url'):
            text = url_read()

        # 입력된 내용을 가지고 ChatGPT에 문제 생성 요청
        gpt(text,user,types)

        # 현재 문서 아이디(이걸로 문제 출제 완료 후 바로 만들어진 문제 페이지로 이동)
        now_doc_id = session.get('now_doc_id')
        target_url = url_for('print_summary', document_id = now_doc_id)
        return redirect(target_url)

    # 문서 삭제
    def doc_delete(document_id):
        db.summaries.delete_one({'_id' : document_id})
        db.questions.delete_many({'doc_id' : document_id})
        db.answers.delete_many({'doc_id' : document_id})
        return redirect('/main')

    # 문제 채점
    def scoring(document_id, answers_dict):
        answer = db.answers.find({'doc_id' : document_id}) # 정답 가져오기
        round_number = len(db.summaries.find_one({'_id':document_id})['round']) # 채점 횟수 업데이트 위함.

        for key in enumerate(answers_dict.keys()):
            # 각 문제에 대한 답을 입력했다면 채점하기 (key[0] : index, key[1] : answer '_id')
            if answer[key[0]]['_id'] == key[1]:
                # 정답
                if answer[key[0]]['answer'].strip() == answers_dict[key[1]].strip():
                    update_data = {"$set" : {"correct" : "right"}}
                    db.answers.update_one({'_id':answer[key[0]]['_id']}, update_data)
                    
                # 오답
                else:
                    update_data = {"$set" : {"correct" : "wrong"}}
                    db.answers.update_one({'_id':answer[key[0]]['_id']}, update_data)
        # 회차에 따른 점수 업데이트
        grade = round(db.answers.count_documents({'doc_id':document_id, 'correct':'right'}) / db.answers.count_documents({'doc_id':document_id}) * 100, 2)
        n_grade = {"$push" : {"round" : round_number, "grade" : grade}}
        db.summaries.update_one({'_id':answer[key[0]]['doc_id']}, n_grade)

        return redirect(url_for('print_summary', document_id=document_id))

    # 리셋
    def reset(document_id):
        db.answers.update_many({'doc_id':document_id},{"$set":{"correct" : "normal"}})
        return redirect(url_for('print_summary', document_id=document_id))