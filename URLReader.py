import requests
from flask import request
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def url_read():
    url = request.form.get('url')
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")
    text = ''
    for p_tag in soup.find_all('p'):
        text += p_tag.get_text()
    return text