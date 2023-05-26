import fitz
import re
import os
from flask import request
from api import gpt
from tqdm import tqdm

def file_read(user, types):
    # 파일 받아와서 저장
    file = request.files['file']
    file_name=file.filename
    os.makedirs('./files', exist_ok=True)
    FILEPATH = os.path.join('./files',file_name)
    file.save(FILEPATH)

    # pdf 내용 읽기
    document_text = fitz.open(FILEPATH)
    print(document_text.get_page_text(pno=2))

    count = 0
    content = ''

    start_pno = 2
    split_count = 15
    for pno in tqdm(range(start_pno, document_text.page_count)):
        text = document_text.get_page_text(pno=pno)
        count += 1
        content += text+' '

        if count == split_count:
            gpt(content, user, types)
            count=0
            content=''
    return