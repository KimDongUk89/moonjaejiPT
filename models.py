from flask import request, redirect, jsonify, session, url_for
from app import db
from api import gpt
import os
from FileReader import file_read
from URLReader import url_read

class User():
    def user_register(self):
        # 현재 로그인한 사용자 아이디를 세션에 저장
        session['now_user_email'] = request.form.get('email')

        # 로그인 정보를 db에 저장하는데, 이미 등록된 id라면 이름이나 프로필 사진이 바꼈는지 확인하고 업데이트, 처음 등록이라면 insert
        data = {
            "id" : request.form.get('email'),
            "name" : request.form.get('name'),
            "profile_image_url" : request.form.get('profile_image_url'),
            "thumbnail_image_url" : request.form.get('thumbnail_image_url')
        }

        filter_query = {"id":data["id"]}
        update_data = {"$set" : {"name" : data["name"], "profile_image_url" : data["profile_image_url"], "thumbnail_image_url" : data["thumbnail_image_url"]}}

        result = db.user.update_one(filter_query, update_data)
        print("back : ", data)
        if result.matched_count == 0:
            db.user.insert_one(data)
            print("data inserted")
        else:
            print("data updated successfully.")

        return redirect('/main/')


class Doc():

    def doc(self,user):
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

        print("text:",text)
        # 입력된 내용을 가지고 ChatGPT에 문제 생성 요청
        gpt(text,user,types)

        now_doc_id = session.get('now_doc_id')
        target_url = url_for('print_summary', document_id = now_doc_id)
        return redirect(target_url)

    def doc_delete(document_id):
        db.summaries.delete_one({'_id' : document_id})
        db.questions.delete_many({'doc_id' : document_id})
        db.answers.delete_many({'doc_id' : document_id})
        return redirect('/main')