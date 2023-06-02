from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# url = request.form.get('url')
# tistory
# url = 'https://on-ai.tistory.com/17'

# velog
# url = 'https://velog.io/@boyunj0226/GPT%ED%95%9C%ED%85%8C-%EC%9E%98-%EB%AC%BC%EC%96%B4%EB%B3%B4%EB%8A%94-%EB%B2%95-2-%EB%8B%A4%EC%96%91%ED%95%9C-Prompt-Engineering-%EB%B0%A9%EB%B2%95'
url = 'https://velog.io/@seyeop03/BeautifulSoup%EC%9D%98-find-findall-%EB%A9%94%EC%86%8C%EB%93%9C'
html = requests.get(url)
bsObject = BeautifulSoup(html.text, "html.parser")

for p_tag in bsObject.find_all('p'):
    print(p_tag.get_text())
