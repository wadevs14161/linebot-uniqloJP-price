import requests
from bs4 import BeautifulSoup

url = "https://www.uniqlo.com/tw/zh_TW/product-detail.html?productCode=u0000000020354"
url = "https://www.google.com"

page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')

print(page.status_code)