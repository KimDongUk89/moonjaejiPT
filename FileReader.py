import pdftotext
import os
from flask import request

def readFile():
    # return 할 텍스트
    text = ''

    # 파일 받아와서 저장
    file = request.files['file']
    file_name=file.filename
    os.makedirs('./files', exist_ok=True)
    FILEPATH = os.path.join('./files',file_name)
    file.save(FILEPATH)

    # pdf 내용 읽기
    file = open(FILEPATH, 'rb')
    fileReader = pdftotext.PDF(file)
    
    for page in fileReader:
        text+=page

    return text