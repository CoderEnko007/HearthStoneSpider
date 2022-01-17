# -*- coding: utf-8 -*-
import scrapy
import json
import platform
import requests
from datetime import datetime

from scrapy import signals
from selenium import webdriver
from pydispatch import dispatcher
from scrapy.http import Request
from HearthStoneSpider.settings import SQL_FULL_DATETIME
from HearthStoneSpider.items import HSArenaCardsSpiderItem
from HearthStoneSpider.tools.ifan import iFanr
from HearthStoneSpider.tools.dbtools import DBManager
from HearthStoneSpider.settings import ARENA_FILES
from HearthStoneSpider.tools.utils import DecimalEncoder

class HSArenaCardsSpider(scrapy.Spider):
    name = 'HSArenaCards'
    allowed_domains = ['hsreplay.net']
    # url = 'https://hsreplay.net/analytics/query/card_list/?GameType=ARENA&TimeRange=LAST_7_DAYS'
    url = 'https://hsreplay.net/analytics/query/card_list/?GameType=ARENA&TimeRange=CURRENT_EXPANSION'
    # url = 'https://hsreplay.net/analytics/query/card_list/?GameType=ARENA&TimeRange=ARENA_EVENT'
    start_urls = [url]

    def __init__(self, params=None, card_hsid=None, local_update=False):
        super(HSArenaCardsSpider, self).__init__()
        self.local_update = eval(local_update)
        if not self.local_update:
            chrome_opt = webdriver.ChromeOptions()
            chrome_opt.add_argument('--disable-gpu')
            chrome_opt.add_argument('--no-sandbox')
            if platform.platform().find('Linux') != -1:
                chrome_opt.add_argument('blink-settings=imagesEnabled=false')  # 无图模式
                chrome_opt.add_argument('--headless')  # 无页面模式
            self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser
        self.ifanr = iFanr()
        self.total_count = 0
        self.scraped_count = 0
        self.temp_count = 0
        self.cards_series = {}
        self.extra_data_flag = True if params=='extra_data' else False
        self.single_card = card_hsid
        self.addCookieFlag = True
        # if params == 'extra_data':
        # with open(file, 'r', encoding='UTF-8') as f:
        #     list = json.load(f)
        #     self.ifanrArenaList = list['data']

    def spider_closed(self):
        now = datetime.now().strftime(SQL_FULL_DATETIME)
        if not self.local_update:
            self.browser.quit()
        print('{0}:HSArenaCards end'.format(now))


    def parse(self, response):
        jsonData = response.css('pre::text').extract_first('')
        try:
            content = json.loads(jsonData).get('series').get('data')
        except Exception as e:
            print('出错了！！', e)
            return
        for faction in content:
            self.total_count += len(content[faction])
        for faction in content:
        # faction = 'ALL'
        #     card_played_list = []
            for item in content[faction]:
                if self.single_card and item.get('dbf_id') != int(self.single_card):
                    continue
                # if item.get('dbf_id')!=60016:
                #     continue
                card = HSArenaCardsSpiderItem()
                card['classification'] = faction
                card['dbfId'] = item.get('dbf_id')
                # card['times_played'] = item.get('total') if item.get('total') else None
                card['times_played'] = item.get('times_played')
                # card['played_pop'] = round(float(item.get('popularity')), 4) if item.get('popularity') else None
                card['deck_pop'] = item.get('included_popularity')
                # card['played_winrate'] = round(item.get('winrate'), 4) if item.get('winrate') else None
                card['deck_winrate'] = item.get('included_winrate')
                card['played_winrate'] = item.get('winrate_when_played')
                card['copies'] = item.get('included_count')
                card['extra_data_flag'] = self.extra_data_flag
                yield card
            #     card_played_list.append(card)
            # self.cards_series[faction] = card_played_list
        # yield Request(url='https://hsreplay.net/analytics/query/card_included_popularity_report_v2/?GameType=ARENA',
        #               callback=self.final_parse, dont_filter=True)

    def final_parse(self, response):
        jsonData = response.css('pre::text').extract_first('')
        content = json.loads(jsonData).get('series').get('data')
        series = self.cards_series
        for faction in series:
            print(faction)
            for item in series[faction]:
                card_played = list(filter(lambda x: x.get('dbf_id') == item['dbfId'], content[faction]))
                if len(card_played)>0:
                    card_played = card_played[0]
                    item['deck_pop'] = round(card_played.get('popularity'), 2) if card_played.get('popularity') else None
                    item['copies'] = card_played.get('count')
                    item['deck_winrate'] = round(card_played.get('winrate'), 2) if card_played.get('winrate') else None
                    item['extra_data_flag'] = self.extra_data_flag
                    yield item
                else:
                    self.total_count -= 1
