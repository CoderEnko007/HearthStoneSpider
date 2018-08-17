# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
import time
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from HearthStoneSpider.items import HSReportSpiderItem
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT

class HSReportSpider(scrapy.Spider):
    name = 'HSReport'
    allowed_domains = ['hsreplay.net']
    start_urls = ['http://hsreplay.net/']

    def __init__(self):
        super(HSReportSpider, self).__init__()
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('blink-settings=imagesEnabled=false') # 无图模式
        chrome_opt.add_argument('--headless') # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed) # scrapy信号量，spider退出时关闭browser

    def spider_closed(self):
        self.browser.close()

    def parse(self, response):
        rank_panel = self.browser.find_elements_by_css_selector('.panel-card.panel-theme-dark.panel-accent-blue')[1]
        rank_panel_btns = rank_panel.find_elements_by_css_selector('a.feature-btn')
        for btn in rank_panel_btns:
            btn.click()
            time.sleep(3)
            print(btn.text)
            rank_node = response.css('ul.class-list.class-ranking li')
            for item in rank_node:
                hs_item = HSReportSpiderItem()
                index = item.css('.class-index::text').extract_first(' ')
                hs_item['rank_no'] = int(re.match('.*(\d).*', index).group(1))
                hs_item['name'] = item.css('.class-name::text').extract_first(' ')
                hs_item['winrate'] = item.css('.class-winrate::text').extract_first(' ')
                hs_item['mode'] = btn.text
                hs_item['date'] = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
                yield hs_item