import json
import datetime
import time
import os
from selenium import webdriver
from scrapy.selector import Selector
from selenium.webdriver.support.select import Select

class web_manager():
    def __init__(self):
        pass

    def get_cookie(self):
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('blink-settings=imagesEnabled=false')  # 无图模式
        chrome_opt.add_argument('--disable-gpu')
        # chrome_opt.add_argument('--headless')  # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        # self.browser = webdriver.Firefox(executable_path='geckodriver')
        self.t_selector = Selector(text=self.browser.page_source)
        self.browser.get("http://hsreplay.net/")
        time.sleep(10)
        self.browser.find_element_by_css_selector("li.button-container a.promo-button").click()
        time.sleep(1)
        Select(self.browser.find_element_by_tag_name('select')).select_by_index(1)
        self.browser.find_element_by_css_selector("button.hero-button").click()
        time.sleep(1)
        # browser.find_element_by_css_selector(".controls input[name='accountName']").send_keys('1993261087@qq.com')
        # browser.find_element_by_css_selector(".controls input[name='password'").send_keys('houxilu0039')
        self.browser.find_element_by_css_selector(".controls input[name='accountName']").send_keys('yf381966217@163.com')
        self.browser.find_element_by_css_selector(".controls input[name='password'").send_keys('YFym258198666')
        self.browser.find_element_by_css_selector("div.submit button").click()
        time.sleep(15)
        # langToggle = self.browser.find_elements_by_css_selector('.dropdown-toggle')[0]
        # langToggle.click()
        # time.sleep(1)
        # langItemEn = self.browser.find_elements_by_css_selector('.dropdown-menu li')[0]
        # langItemEn.click()
        # time.sleep(1)
        self.browser.get("http://hsreplay.net/")
        dictCookies = self.browser.get_cookies()
        jsonCookies = json.dumps(dictCookies)
        filename = os.path.join(os.path.abspath('.'), 'cookies.json')
        with open(filename, 'w') as f:
            try:
                f.write(jsonCookies)
            except Exception as e:
                print(e)

    def check_cookie(self, path):
        with open(path, 'r') as f:
            listCookies = json.loads(f.read())
        for cookie in listCookies:
            now = datetime.datetime.now()
            if cookie.get('expiry'):
                expiry = datetime.datetime.utcfromtimestamp(cookie['expiry'])
                diff = expiry - now
                str = "条目名称：{0}，值：{1}".format(cookie['name'], cookie['value'])
                print(str)
                str = "{0}:现在时间:{1}，过期时间:{2}，距离过期还剩:{3}".format(cookie['name'], now, expiry, diff)
                print(str)

if __name__ == '__main__':
   obj = web_manager()
   obj.get_cookie()
   # filename = os.path.join(os.path.abspath('.'), 'cookies.json')
   # obj.check_cookie(filename)

   # driver = webdriver.Firefox(executable_path='geckodriver')
   # driver.get('https://www.baidu.com')
   # print(driver.current_url)