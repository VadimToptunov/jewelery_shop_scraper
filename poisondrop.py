import csv

import requests
from seleniumwire import webdriver

origin = "<here_should_be_a_site_name>"
main_url = f"{origin}/catalog/"


def get_cookies():
    driver = webdriver.Chrome(executable_path='./drivers/chromedriver')
    driver.get(main_url)
    button_yes = driver.find_element_by_css_selector('button.location-detect__button._yes')
    button_yes.click()
    tokens = []
    for req in driver.requests:
        if str(req).endswith("show"):
            x_xsrf_token = req.headers.get('X-XSRF-TOKEN')
            cookie = req.headers.get('Cookie')
            tokens.append(x_xsrf_token)
            tokens.append(cookie)
    driver.quit()
    return tokens


def get_full_response(session, xsrf_token, poison_drop, csrf, offset):
    cookies = {
        'XSRF-TOKEN': xsrf_token,
        'poisondrop_session': poison_drop,
        'pages-count': '3',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json;charset=utf-8',
        'X-XSRF-TOKEN': csrf,
        'Origin': origin,
        'Connection': 'keep-alive',
        'Referer': main_url,
    }

    data = '{"url":"","limit":48,"offset":' + str(offset) + ',"parameters":{"section":""}}'

    response = session.post(f'{main_url}show', headers=headers, cookies=cookies, data=data)
    return response.json()


def request_jewelery_shop():
    tokens = get_cookies()
    csrf = tokens[0]
    xsrf_token = str(tokens[1]).split(";")[0].split("=")[1]
    poison_drop = str(tokens[1]).split(";")[1].split("=")[1]
    session = requests.Session()
    full_response = get_full_response(session, xsrf_token, poison_drop, csrf, 0)
    quantity = full_response.get('result').get('quantity')
    with open('shop_data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(("Product url", "Designer", "Product name", "Price"))
        for offset in range(0, quantity, 48):
            full_response = get_full_response(session, xsrf_token, poison_drop, csrf, offset)
            products = full_response.get('result').get('products')
            for product in products:
                product_url = f'{main_url}{product.get("catalog").get("url")}/{product.get("url")}'
                designer_name = product.get('designer').get('name')
                product_name = product.get('name')
                price = str(product.get('price').get('initial')) + ' руб.'
                csv_writer.writerow((product_url, designer_name, product_name, price))


if __name__ == "__main__":
    request_jewelery_shop()
