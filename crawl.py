import requests
from bs4 import BeautifulSoup

def product_crawl(serial_number):
    product_base = 'https://www.uniqlo.com/jp/ja/products/'
    product_url = product_base + serial_number
    # first check if product exist in UniqloJP
    product_page = requests.get(product_url)
    if product_page.status_code == 404:
        try:
            product_info_api_url = "https://www.uniqlo.com/jp/api/commerce/v5/ja/products?q={}&queryRelaxationFlag=true&offset=0&limit=36&httpFailure=true".format(serial_number)
            product_info_page = requests.get(product_info_api_url)
            json_input = product_info_page.json()
            if json_input['status'] == "ok":
                # product_list = []
                serial_alt = json_input['result']['relaxedQueries'][0]
                serial_number = json_input['result']['items'][0]['productId']
                serial_number = serial_number[1:7]
                product_url = product_base + serial_number
                price_jp = json_input['result']['items'][0]['prices']['base']['value']

                # currency exchange
                currency_url = "https://www.google.com/finance/quote/JPY-TWD"
                currency_page = requests.get(currency_url)
                soup = BeautifulSoup(currency_page.text, "lxml")
                exchange_rate = float(soup.find('div', class_='YMlKec fxKbKc').get_text())
                #price_jp = int(product_list[0]['price'])
                jp_price_in_twd = round(price_jp * exchange_rate)

                uq_url = "https://uq.goodjack.tw/search?query=" + serial_alt
                url = requests.get(uq_url).url
                product_code_tw = url[-14:]

                product_info_tw_url = "https://d.uniqlo.com/tw/p/product/i/product/spu/pc/query/" + product_code_tw + "/zh_TW"
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                product_info_tw = requests.get(product_info_tw_url, headers=headers)

                json_input_tw = product_info_tw.json()
                price_tw = []
                if json_input_tw['success']:
                    price_original = json_input_tw['resp'][0]['summary']['originPrice']
                    price_min = json_input_tw['resp'][0]['summary']['minPrice']
                    price_max = json_input_tw['resp'][0]['summary']['maxPrice']
                    price_tw.append(int(price_original))
                    price_tw.append(int(price_min))
                    price_tw.append(int(price_max))

                result = [serial_number, product_url, price_jp, jp_price_in_twd, price_tw]
                return result
        except:
            return -1
    # search price_jp in product page (new method, 10-Apr.-2024)
    elif product_page:
        product_info_api_url = "https://www.uniqlo.com/jp/api/commerce/v5/ja/products/E{}-000/price-groups/00/l2s?withPrices=true&withStocks=true&includePreviousPrice=false&httpFailure=true".format(serial_number)
        product_info_page = requests.get(product_info_api_url)
        json_input = product_info_page.json()

        price_list = []
        product_stock = {
            'XS': 0,
            'S': 0,
            'M': 0,
            'L': 0,
            'XL': 0,
            'XXL': 0,
            '3XL': 0,
            '4XL': 0,
        }

        for size in json_input['result']['prices']:
            price_list.append(json_input['result']['prices'][size]['base']['value'])

        # product list
        product_list = []
        for item in json_input['result']['l2s']:
            # product dict
            product_dict = {}
            product_dict['serial'] = serial_number
            product_dict['serial_alt'] = item['communicationCode'][:6]       
            product_dict['id'] = item['l2Id']

            # Add color
            color_code = int(item['color']['code'][-2:])
            if color_code <= 1:
                color = 'White 白'
            elif color_code < 9:
                color = 'Gray 灰'
            elif color_code == 9:
                color = 'Black 黑'
            elif color_code <= 19:
                color = 'Red 紅'
            elif color_code <= 29:
                color = 'Orange 橘'
            elif color_code <= 39:
                color = 'Brown 棕'
            elif color_code <= 49:
                color = 'Yellow 黃'
            elif color_code <= 59:
                color = 'Green 綠'
            elif color_code < 69:
                color = 'Blue 藍'
            elif color_code == 69:
                color = 'Navy 海軍藍'
            elif color_code <= 79:
                color = 'Purple 紫'
            else:
                color = 'Others 其他'
            product_dict['color'] = color
            
            # Add size
            size_code = int(item['size']['code'][-3:])
            size = ""
            if size_code == 1:
                size = "XXS"
            elif size_code == 2:
                size = "XS"
            elif size_code == 3:
                size = "S"
            elif size_code == 4:
                size = "M"
            elif size_code == 5:
                size = "L"
            elif size_code == 6:
                size = "XL"
            elif size_code == 7:
                size = "XXL"
            elif size_code == 8:
                size = "3XL"
            elif size_code == 9:
                size = "4XL"
            elif size_code == 10:
                size = "5XL"

            product_dict['size'] = size

            # Append product to product list
            product_list.append(product_dict)

        
        # Add stock status
        for dict in product_list:
            if dict['id'] in json_input['result']['stocks']:
                dict['stock'] = json_input['result']['stocks'][dict['id']]['statusCode']
        # Add price
        for dict in product_list:
            if dict['id'] in json_input['result']['prices']:
                dict['price'] = json_input['result']['prices'][dict['id']]['base']['value']

        # currency exchange
        currency_url = "https://www.google.com/finance/quote/JPY-TWD"
        currency_page = requests.get(currency_url)
        soup = BeautifulSoup(currency_page.text, "lxml")
        exchange_rate = float(soup.find('div', class_='YMlKec fxKbKc').get_text())
        price_jp = int(product_list[0]['price'])
        jp_price_in_twd = round(price_jp * exchange_rate)


        uq_url = "https://uq.goodjack.tw/search?query=" + serial_number
        url = requests.get(uq_url).url
        product_code_tw = url[-14:]

        product_info_tw_url = "https://d.uniqlo.com/tw/p/product/i/product/spu/pc/query/" + product_code_tw + "/zh_TW"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        product_info_tw = requests.get(product_info_tw_url, headers=headers)

        json_input_tw = product_info_tw.json()
        price_tw = []
        if json_input_tw['success']:
            price_original = json_input_tw['resp'][0]['summary']['originPrice']
            price_min = json_input_tw['resp'][0]['summary']['minPrice']
            price_max = json_input_tw['resp'][0]['summary']['maxPrice']
            price_tw.append(int(price_original))
            price_tw.append(int(price_min))
            price_tw.append(int(price_max))
      
        result = [serial_number, product_url, price_jp, jp_price_in_twd, price_tw, product_list]

        return result

            
# test, product list = [464787, 467536, 467543, 459591, 450314]
if __name__ == '__main__':
    serial_number = '470989'
    print(product_crawl(serial_number))
    
