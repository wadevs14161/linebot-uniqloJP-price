import requests
from bs4 import BeautifulSoup


def fetch_exchange_rate():
    """Fetch the current JPY to TWD exchange rate."""
    try:
        currency_url = "https://www.google.com/finance/quote/JPY-TWD"
        currency_page = requests.get(currency_url)
        soup = BeautifulSoup(currency_page.text, "html.parser")
        return float(soup.find('div', class_='YMlKec fxKbKc').get_text())
    except Exception:
        return None


def get_color_name(color_code):
    color_code = int(color_code)
    if color_code <= 1:
        return 'White 白'
    elif color_code < 9:
        return 'Gray 灰'
    elif color_code == 9:
        return 'Black 黑'
    elif color_code <= 19:
        return 'Red 紅'
    elif color_code <= 29:
        return 'Orange 橘'
    elif color_code <= 39:
        return 'Brown 棕'
    elif color_code <= 49:
        return 'Yellow 黃'
    elif color_code <= 59:
        return 'Green 綠'
    elif color_code < 69:
        return 'Blue 藍'
    elif color_code == 69:
        return 'Navy 海軍藍'
    elif color_code <= 79:
        return 'Purple 紫'
    return 'Others 其他'


def get_size_name(size_code):
    size_dict = {
        1: "XXS", 2: "XS", 3: "S", 4: "M", 5: "L", 6: "XL", 7: "XXL",
        8: "3XL", 9: "4XL", 23: "23-25", 25: "25-27", 27: "27-29",
        60: "60", 70: "70", 80: "80", 90: "90", 100: "100", 110: "110",
        120: "120", 130: "130", 140: "140", 150: "150", 160: "160",
        499: "AA 65/70", 500: "AB 65/70", 501: "CD 65/70", 502: "EF 65/70",
        503: "AB 75/80", 504: "CD 75/80", 505: "EF 75/80",
        506: "AB 85/90", 507: "CD 85/90", 508: "EF 85/90"
    }
    return size_dict.get(int(size_code), "")


def product_crawl(serial_number):
    product_all_info = {
        "serial_number": "",
        "product_url": "",
        "page_title": "",
        "price_jp": 0,
        "jp_price_in_twd": 0,
        "price_tw": [],
        "product_list": []
    }

    base_url = 'https://www.uniqlo.com/jp/ja/products/'
    product_url = base_url + serial_number
    response = requests.get(product_url)
    
    # Ensure proper UTF-8 encoding for Japanese characters
    if response.status_code == 200:
        response.encoding = 'utf-8'

    # Get the web page title
    page_title = ""
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                page_title = title_tag.get_text().strip()
                print(f"Page title: {page_title}")
        except Exception as e:
            print(f"Error getting page title: {e}")

    # Case 1: Product not found on JP site, directly find product on API
    if response.status_code == 404:
        print("Product not found on JP site, trying alternative API.")
        try:
            alt_api_url = f"https://www.uniqlo.com/jp/api/commerce/v5/ja/products?q={serial_number}&queryRelaxationFlag=true&offset=0&limit=36&httpFailure=true"
            api_resp = requests.get(alt_api_url).json()

            if api_resp.get('status') == "ok":
                serial_alt = api_resp['result']['relaxedQueries'][0]
                item = api_resp['result']['items'][0]
                serial_number = item['productId'][1:7]
                # Execute product_crawl again with the new serial number
                print(f"Found alternative serial number: {serial_number}")
                return product_crawl(serial_number)
        except Exception:
            return -1

    # Case 2: Product found
    try:
        detail_url = f"https://www.uniqlo.com/jp/api/commerce/v5/ja/products/E{serial_number}-000/price-groups/00/l2s?withPrices=true&withStocks=true&includePreviousPrice=false&httpFailure=true"
        detail_resp = requests.get(detail_url).json()

        price_jp = None
        product_list = []

        for item in detail_resp['result']['l2s']:
            l2_id = item['l2Id']
            color = get_color_name(item['color']['code'][-2:])
            size = get_size_name(item['size']['code'][-3:])

            stock = detail_resp['result']['stocks'].get(l2_id, {}).get('statusCode', 0)
            price = detail_resp['result']['prices'].get(l2_id, {}).get('base', {}).get('value', 0)

            if price_jp is None:
                price_jp = price

            product_list.append({
                "serial": serial_number,
                "serial_alt": item['communicationCode'][:6],
                "id": l2_id,
                "color": color,
                "size": size,
                "stock": stock,
                "price": price
            })

        rate = fetch_exchange_rate()
        jp_price_in_twd = round(price_jp * rate) if rate else 0

        product_all_info.update({
            "serial_number": serial_number,
            "product_url": product_url,
            "page_title": page_title,
            "price_jp": price_jp,
            "jp_price_in_twd": jp_price_in_twd,
            "product_list": product_list
        })

        return product_all_info

    except Exception:
        return -1

            
# test, product list = [464787, 467536, 467543, 459591, 450314]
if __name__ == '__main__':
    serial_number = '474479'
    print(product_crawl(serial_number))
    
