import requests
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def readURL(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")
    text = ''
    # url에서 <p>태그에 담긴 내용 모두 가져오기
    for p_tag in soup.find_all('p'):
        text += p_tag.get_text()
    return text


