# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import copy
from datetime import datetime

from scrapy import signals
from selenium import webdriver
from pydispatch import dispatcher
from scrapy.http import Request
from HearthStoneSpider.settings import SQL_FULL_DATETIME
from HearthStoneSpider.items import HSRankingSpiderItem

class HSRankingSpider(scrapy.Spider):
    name = 'HSRanking'
    allowed_domains = ['hsreplay.net']
    start_urls = ['https://hsreplay.net/analytics/query/player_class_performance_summary/']

    def __init__(self, local_update=False):
        super(HSRankingSpider, self).__init__()
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('blink-settings=imagesEnabled=false')  # 无图模式
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--no-sandbox')
        chrome_opt.add_argument('--headless')  # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)
        self.addCookieFlag = False
        self.local_update = local_update

    def spider_closed(self):
        now = datetime.now().strftime(SQL_FULL_DATETIME)
        print('{0}:HSRanking end'.format(now))
        self.browser.quit()

    def engine_stopped(self):
        print('HSRanking engine end')
        # 炉石传说情报站webhook
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/ndhvGONeNt')
        # 炉石数据可视化webhook
        # requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/T1vA85AhPG')

    def parse(self, response):
        game_type = {'Standard': 2, 'Wild': 30, 'Arena': 3, 'Classic': 58, 'Duels': 55}
        print('response:', response.status, response.text)
        jsonData = response.css('pre::text').extract_first('')
        try:
            content = json.loads(jsonData).get('series').get('data')
        except Exception as e:
            print('出错了！！',e)
            # print('response:', response.status, response.text)
            # print('jsonData:', jsonData)
            # return
            jsonData = requests.get('https://hsreplay.net/analytics/query/player_class_performance_summary/').text
            content = json.loads(jsonData).get('series').get('data')
        for faction in content:
            for item in content[faction]:
                rank_item = HSRankingSpiderItem()
                if faction.lower() == 'demonhunter':
                    rank_item['faction'] = 'DemonHunter'
                else:
                    rank_item['faction'] = faction.capitalize()
                rank_item['game_type'] = list(game_type.keys())[list(game_type.values()).index(item.get('game_type'))]
                rank_item['popularity'] = float('%.2f' % item.get('popularity')) if item.get('popularity') else None
                rank_item['win_rate'] = float('%.2f' % item.get('win_rate'))
                rank_item['total_games'] = item.get('total_games') if item.get('popularity') else None
                rank_item['date'] = datetime.now().strftime(SQL_FULL_DATETIME)
                yield rank_item
                # if rank_item['popularity'] is None:
                #     yield Request(url='https://hsreplay.net/analytics/query/archetype_popularity_distribution_stats_v2/',
                #         meta=rank_item, callback=self.parse_pop, dont_filter=True)
                # else:
                #     yield rank_item
    # def parse_pop(self, response):
    #     rank_item = copy.copy(response.meta)
    #     jsonData = response.css('pre::text').extract_first('')
    #     content = json.loads(jsonData).get('series').get('data')
    #     list_content = [item for sublist in [x for x in content.values()] for item in sublist]
    #     total_games = sum([x['total_games'] for x in list_content])
    #     for faction in rank_item:
    #         item = rank_item[faction]
    #         faction = faction.upper()
    #         contentItem = content[faction]
    #         item['total_games'] = sum([x['total_games'] for x in contentItem])
    #         item['popularity'] = round(item['total_games']/total_games, 2)
    #     yield rank_item