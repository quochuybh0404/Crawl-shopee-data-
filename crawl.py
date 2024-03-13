from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import re
import time


# # # vào cmd gõ "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\localhost"
### Đăng nhập vào chrome rồi chạy đoạn code bên dưới
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress","localhost:9222")
driver = webdriver.Chrome(options=options)
###### Crawl theo từ khóa "quần áo"
driver.get("https://shopee.vn/search?keyword=qu%E1%BA%A7n%20%C3%A1o&page=0")
time.sleep(4)

list_names = []
list_prices = []
list_links = []
list_amount = []
list_ratings = []
list_locations = []

total_page = int(driver.find_element(By.CLASS_NAME, 'shopee-mini-page-controller__total').text)
for num_page in range(0,total_page):
    for _ in range(6):
    # Cuộn trang xuống
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(3)
    info_elements = driver.find_elements(By.CSS_SELECTOR,'ul.row.shopee-search-item-result__items > li')
    for info_element in info_elements:
        time.sleep(3)
        ### --- Tên sản phẩm ---
        product_name_element = info_element.find_element(By.CSS_SELECTOR, '.xA2DZd.tYvyWM.wupGTj')
        product_name = product_name_element.text
        # print(product_name)
        list_names.append(product_name)

        ### --- Giá tiền ---
        price_element = info_element.find_element(By.CLASS_NAME, '_7s1MaR')
        price = price_element.text
        list_prices.append(price)

        ### --- Lấy link sản phẩm ---
        link_element = info_element.find_element(By.CSS_SELECTOR, 'a[data-sqe="link"]')
        link_href = link_element.get_attribute('href')
        list_links.append(link_href)

        ### --- Lấy số lượng sản phẩm đã bán ---
        try: 
            quantity_element = info_element.find_element(By.CSS_SELECTOR, '.L68Ib9.s3wNiK')
            string_split  = re.search(r'(\d+([,.]\d+)?)([kK]|\b)', quantity_element.text).group() # Tách chuỗi "Đã bán xx" --> xx
            if string_split[-1].isalpha():
                quantity  = int(float(string_split[:-1].replace(',', '.')) * 1000)
                list_amount.append(quantity)
            else:
                quantity = int(string_split)
                list_amount.append(quantity)
        except NoSuchElementException: ## chưa bán được sản phẩm thì sẽ ko có class= L68Ib9 s3wNiK
            quantity = 0
            list_amount.append(quantity)
            
        ### --- Lấy điểm số sản phẩm ---
        rating = 0 
        try:
            rating_star_element = info_element.find_element(By.CLASS_NAME, "shopee-rating-stars__stars")
            star_element = rating_star_element.find_elements(By.CLASS_NAME, "shopee-rating-stars__star-wrapper")
            for element in star_element:
                element_lit = element.find_element(By.CLASS_NAME, "shopee-rating-stars__lit")
                width_style = element_lit.get_attribute("style")
                # print(width_style)
                width_percentage = float(width_style.split(':')[1].strip('%;')) / 100
                rating += width_percentage
            rating = round(rating, 1)
            list_ratings.append(rating)
        except NoSuchElementException: ## chưa bán được sản phẩm thì sẽ ko có  class = shopee-rating-stars__stars
            list_ratings.append(float(rating))

        ### --- Lấy địa điểm ---
        try:
            location_elements = info_element.find_element(By.CLASS_NAME, "wZEyNc")
            location = location_elements.text
            list_locations.append(location)
        except NoSuchElementException: ## Có 1 sản phẩm ko có để địa chỉ trên giao diện
            location = ""
            list_locations.append(location)

    ### --- Sang trang ---
    driver.get("https://shopee.vn/search?keyword=qu%E1%BA%A7n%20%C3%A1o&page=" + str(num_page+1))
    time.sleep(3)


print(len(list_names))
print(len(list_prices))
print(len(list_links))
print(len(list_amount))
print(len(list_ratings))
print(len(list_locations))

dict_product = {
    'names': list_names,
    'prices': list_prices,
    'links': list_links,
    'amount': list_amount,
    'ratings': list_ratings,
    'locations': list_locations,
    }


import csv
with open('data/crawl_Shopee.csv', 'w', encoding = 'utf-8') as f:
    write = csv.writer(f)
    write.writerow(dict_product.keys())
    write.writerows(zip(*dict_product.values()))