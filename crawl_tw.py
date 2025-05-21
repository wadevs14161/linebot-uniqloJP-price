import requests

serial_number = "457543"

uq_url = "https://uq.goodjack.tw/search?query=" + serial_number
url = requests.get(uq_url).url
print(url)
product_code_tw = url[-14:]

# This url is invalid, 20/09/2024
product_info_tw_url = "https://d.uniqlo.com/tw/p/product/i/product/spu/pc/query/" + product_code_tw + "/zh_TW"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
product_info_tw = requests.get(product_info_tw_url, headers=headers)

print(product_info_tw.url)
json_input_tw = product_info_tw.json()
price_tw = []
if json_input_tw['success']:
    price_original = json_input_tw['resp'][0]['summary']['originPrice']
    price_min = json_input_tw['resp'][0]['summary']['minPrice']
    price_max = json_input_tw['resp'][0]['summary']['maxPrice']
    price_tw.append(int(price_original))
    price_tw.append(int(price_min))
    price_tw.append(int(price_max))
