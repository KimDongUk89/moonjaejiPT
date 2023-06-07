import re

f = open('test.txt', 'r')
text = f.read()

# 데이터를 파싱하기 위한 정규표현식
question_pattern = re.compile(r'문제 \d+: ([\s\S]*?)(?=(?:답|문제 \d+:))', re.M)
answer_pattern = re.compile(r'답: ([\s\S]*?)(?=해설)', re.M)
explanation_pattern = re.compile(r'해설: ([\s\S]*?)(?=문제 \d+:|$)', re.M)

# 각 카테고리에 대해 데이터를 분류
questions = re.findall(question_pattern, text)
answers = re.findall(answer_pattern, text)
explanations = re.findall(explanation_pattern, text)

# 결과 출력
print('Questions:', questions)
print('Answers:', answers)
print('Explanations:', explanations)

f.close()