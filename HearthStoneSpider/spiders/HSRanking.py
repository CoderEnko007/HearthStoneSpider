# -*- coding: utf-8 -*-
import scrapy
import json
import requests
from datetime import datetime

from scrapy import signals
from pydispatch import dispatcher
from HearthStoneSpider.settings import SQL_FULL_DATETIME
from HearthStoneSpider.items import HSRankingSpiderItem

class HSRankingSpider(scrapy.Spider):
    name = 'HSRanking'
    allowed_domains = ['hsreplay.net']
    start_urls = ['https://hsreplay.net/analytics/query/player_class_performance_summary/']

    def __init__(self):
        super(HSRankingSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)

    def spider_closed(self):
        now = datetime.now().strftime(SQL_FULL_DATETIME)
        print('{0}:HSRanking end'.format(now))

    def engine_stopped(self):
        print('HSRanking engine end')
        # 炉石传说情报站webhook
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/ndhvGONeNt')
        # 炉石数据可视化webhook
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/T1vA85AhPG')

    def parse(self, response):
        game_type = {'Standard': 2, 'Wild': 30, 'Arena': 3}
        content = json.loads(response.body).get('series').get('data')
        for faction in content:
            for item in content[faction]:
                rank_item = HSRankingSpiderItem()
                rank_item['faction'] = faction.capitalize()
                rank_item['game_type'] = list(game_type.keys())[list(game_type.values()).index(item.get('game_type'))]
                rank_item['popularity'] = float('%.2f' % item.get('popularity'))
                rank_item['win_rate'] = float('%.2f' % item.get('win_rate'))
                rank_item['total_games'] = item.get('total_games')
                rank_item['date'] = datetime.now().strftime(SQL_FULL_DATETIME)
                yield rank_item