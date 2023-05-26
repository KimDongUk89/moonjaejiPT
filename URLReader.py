from urllib.request import urlopen
from flask import request
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def url_read():
    url = request.form.get('url')
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    result = soup.get_text()
    return result