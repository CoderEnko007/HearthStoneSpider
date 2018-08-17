from selenium import webdriver
from scrapy.selector import Selector


chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option("prefs", prefs)
chrome_opt.add_argument('--headless') # 无页面模式

# browser = webdriver.Chrome(chrome_options=chrome_opt)
browser = webdriver.PhantomJS()
browser.get("https://detail.tmall.com/item.htm?spm=a230r.1.14.3.yYBVG6&id=538286972599&cm_id=140105335569ed55e27b&abbucket=15&sku_properties=10004:709990523;5919063:6536025")
# t_selector = Selector(text=browser.page_source)
# print(t_selector.css(".tm-price::text").extract())
print(browser.page_source)
browser.quit()
# browser.get("http://hsreplay.net/")
# import time
# time.sleep(3)
# for i in range(3):
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
#     time.sleep(3)
# rank_panel = browser.find_elements_by_css_selector('.panel-card.panel-theme-dark.panel-accent-blue')[1]
# btns = rank_panel.find_elements_by_css_selector('a.feature-btn')
# for btn in btns:
#     print(btn.text)
#     btn.click()
#     time.sleep(3)
# rank_panel_btns = browser.find_element_by_css_selector('div.row.content-row.features>div.col-lg-4:nth-child(3)')
# for item in rank_panel_btns:
#     print(item)
# t_selector = Selector(text=browser.page_source)
# rank_node = t_selector.css("ul.class-list.class-ranking li")
# for item in rank_node:
#     index = item.css('.class-index::text').extract_first('')
#     name = item.css('.class-name::text').extract_first('')
#     rate = item.css('.class-winrate::text').extract_first('')
#     print(index, name, rate)
# browser.quit()

# 设置chromedriver不加载图片
# chrome_opt = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images":2}
# chrome_opt.add_experimental_option("prefs", prefs)
#
# browser = webdriver.Chrome(executable_path="E:/web_workspace/web_scraper/tools/chromedriver.exe",chrome_options=chrome_opt)
# browser.get("https://www.oschina.net/blog")
