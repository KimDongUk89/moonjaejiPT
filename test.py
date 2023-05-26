from urllib.request import urlopen
from flask import request
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

url = request.form.get('url')
html = urlopen(url)
bsObject = BeautifulSoup(html, "html.parser")