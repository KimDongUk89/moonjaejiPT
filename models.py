from flask import request, jsonify
from app import db
from api import gpt
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
        update_data = {"$set" : {"name" : data["name"], "profile_image_url" : data["profile_image_url"], 
        "thumbnail_image_url" : data["thumbnail_image_url"], "access_token" : data['access_token']}}

        result = db.user.update_one(filter_query, update_data)

        # db에 저장되어 있는 사용자가 없다면 등록
        if result.matched_count == 0:
            db.user.insert_one(data)
            return jsonify(data['_id'])
        # 이미 있다면 업데이트한거
        else:
            user_id = db.user.find_one({"id":data["id"], "platform":data["platform"]})['_id']

            return jsonify(user_id)

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
        db.summaries.update_one({"_id":document_id},{"$set":{"title":summary['title'][:11]}} )

        data_list = []
        # 각 문제에 대해 package 구성(문제 아이디 + 문제 + 정답 + 해설 + 사용자 입력 값 + 메모)
        for question in questions:
            question_id = question.get('_id')

            answer = db.answers.find_one({"question_id":question_id})
            explanation = db.explanations.find_one({"question_id":question_id})

            if question['type'] == 'MULTIPLE CHOICE':
                question_data = question['question']
                result = question_data.split('\n')


                data = {
                    'question_id' : question_id,
                    'question' : result[0],
                    'a':result[1],
                    'b':result[2],
                    'c':result[3],
                    'd':result[4],
                    'answer' : answer['answer'],
                    'explanation' : explanation['explanation'],
                    'user_select' : answer['user_select'],
                    'memo' : question['memo'],
                    'type' : question['type']
                }
            else:
                data = {
                    'question_id' : question_id,
                    'question' : question['question'],
                    'answer' : answer['answer'],
                    'explanation' : explanation['explanation'],
                    'user_select' : answer['user_select'],
                    'memo' : question['memo'],
                    'type' : question['type']
                }
            data_list.append(data)

        response = {
            'summary' : summary['summary'], # 요약본 내용
            'title' : summary['title'],
            'condition' : summary['condition'], # 문서가 채점상태인지 아닌지 ("scored","unscored")
            'data' : data_list, # 위에서 만든 packages
            'data_num' : questions_count # 전체 문제 개수
        }
    
        return jsonify(response)

    def createDoc(self):
        # 선택된 문제 유형
        types = []
        text=''
        
        if request.form.get('multiple choice')=='true':
            types.append('MULTIPLE CHOICE')
        
        if request.form.get('single term answer')=='true':
            types.append('SINGLE TERM ANSWER')

        if request.form.get('fill-in-the-blank')=='true':
            types.append('FILL-IN-THE-BLANK')
        
        if request.form.get('true or false')=='true':
            types.append('TRUE OR FALSE')

        if 'doc' in request.form and request.form.get('doc') != '':
            text = request.form.get('doc')

        elif 'url' in request.form and request.form.get('url') != '':
            text = readURL(request.form.get('url'))

        elif 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                text = readFile(file)
        
        user = request.form.get('user_id')
        print(text)
        result = gpt(text, user, types)
        
        return jsonify(result)



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
            try:
                percent = round(db.questions.count_documents({'doc_id':document_id, 'type':type, 'condition':'right'}) / db.questions.count_documents({'doc_id':document_id, 'type':type}) * 100)
            except:
                pass
            data = {
                type : percent
            }
            data_list.append(data)
    
        db.summaries.update_one({"_id":document_id},{"$push":{"score":data_list}})


        round_num = len(db.summaries.find_one({'_id':document_id})['score']) # 채점 횟수
        history = db.summaries.find_one({'_id':document_id})['score']

        result = []
        for round_num, score_list in enumerate(history, start=1):
            score_data = {
                round_num : score_list
            }
            result.append(score_data)
        # db.summaries.update_one({'_id':document_id}, {"$set":{"score":[]}})
        # db.questions.update_many({'doc_id':document_id},{"$set":{"condition" : "normal"}})
        # db.answers.update_many({'doc_id':document_id}, {"$set":{"user_select":""}})
        # db.summaries.update_one({'_id':document_id}, {"$set":{"condition":"unscored"}})
        return jsonify(result)

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
    def save(user_select):
        # 사용자가 입력한 값 저장
        for package in user_select["packages"]:
            print(package)
            db.questions.update_many({'question_id':package['question_id']}, {'$set':{"user_select":package['user_select'], "memo":package['memo']}})
        return "Save Success"