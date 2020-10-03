# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
import time
import requests
from selenium import webdriver
from pydispatch import dispatcher
from scrapy.selector import Selector
from scrapy import signals

from HearthStoneSpider.items import HSReportSpiderItem, HSRankingSpiderItem
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME

class HSReportSpider(scrapy.Spider):
    name = 'HSReport'
    allowed_domains = ['hsreplay.net']
    start_urls = ['http://hsreplay.net/']

    def __init__(self):
        super(HSReportSpider, self).__init__()
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--no-sandbox')
        chrome_opt.add_argument('blink-settings=imagesEnabled=false') # 无图模式
        chrome_opt.add_argument('--headless') # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed) # scrapy信号量，spider退出时关闭browser
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)

    def spider_closed(self):
        print('HSReport end')
        self.browser.quit()

    def engine_stopped(self):
        print('HSReport engine end')
        # requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/BZ0LYstkuC')
        # 炉石传说情报站webhook
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/ndhvGONeNt')
        # 炉石数据可视化webhook
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/T1vA85AhPG')

    def parse(self, response):
        game_type = ['Standard', 'Wild', 'Arena']
        rank_panel = self.browser.find_elements_by_css_selector('.panel-card.panel-theme-dark.panel-accent-blue')[1]
        rank_panel_btns = rank_panel.find_elements_by_css_selector('a.feature-btn')
        for index, btn in enumerate(rank_panel_btns):
            btn.click()
            time.sleep(2)
            t_selector = Selector(text=self.browser.page_source)
            rank_node = t_selector.css('ul.class-list.class-ranking li')
            for item in rank_node:
                hs_item = HSRankingSpiderItem()
                faction = item.css('.color-overlay::attr(class)').extract_first('')
                # print(faction)
                # hs_item['faction'] = item.css('.class-name::text').extract_first('').replace(' ', '')
                hs_item['faction'] = faction.split(' ')[1].capitalize() if faction.split(' ')[1].lower()!='demonhunter' else 'DemonHunter'
                hs_item['game_type'] = game_type[index]
                # if btn.text.lower().find('standard'):
                #     hs_item['game_type'] = 'Standard'
                # elif btn.text.lower().find('wild'):
                #     hs_item['game_type'] = 'Wild'
                # elif btn.text.lower().find('arena'):
                #     hs_item['game_type'] = 'Arena'
                winrate = item.css('.class-winrate::text').extract_first('')
                hs_item['win_rate'] = float('%.2f' % float(winrate.replace('%', '')))
                hs_item['date'] = datetime.datetime.now().strftime(SQL_FULL_DATETIME)
                # hs_item = HSReportSpiderItem()
                # index = item.css('.class-index::text').extract_first(' ')
                # hs_item['rank_no'] = int(re.match('.*(\d).*', index).group(1))
                # hs_item['name'] = item.css('.class-name::text').extract_first(' ')
                # hs_item['winrate'] = item.css('.class-winrate::text').extract_first(' ')
                # hs_item['mode'] = btn.text
                # hs_item['date'] = datetime.datetime.now().strftime(SQL_FULL_DATETIME)
                hs_item['popularity'] = None
                hs_item['total_games'] = None
                yield hs_item