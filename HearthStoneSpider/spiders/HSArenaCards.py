# -*- coding: utf-8 -*-
import scrapy
import json
import copy
from datetime import datetime

from scrapy import signals
from pydispatch import dispatcher
from scrapy.http import Request
from HearthStoneSpider.settings import SQL_FULL_DATETIME
from HearthStoneSpider.items import HSArenaCardsSpiderItem
from HearthStoneSpider.tools.ifan import iFanr

class HSArenaCardsSpider(scrapy.Spider):
    name = 'HSArenaCards'
    allowed_domains = ['hsreplay.net']
    start_urls = ['https://hsreplay.net/analytics/query/card_played_popularity_report/?GameType=ARENA&TimeRange=LAST_14_DAYS']

    def __init__(self):
        super(HSArenaCardsSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser
        self.ifanr = iFanr()
        self.cards_series = {}

    def spider_closed(self):
        now = datetime.now().strftime(SQL_FULL_DATETIME)
        print('{0}:HSArenaCards end'.format(now))

    def parse(self, response):
        content = json.loads(response.body).get('series').get('data')
        for faction in content:
            card_played_list = []
            for item in content[faction]:
                card = {}
                card['classification'] = faction
                card['dbfId'] = item.get('dbf_id')
                card['times_played'] = item.get('total') if item.get('total') else None
                card['played_pop'] = round(float(item.get('popularity')), 4) if item.get('popularity') else None
                card['played_winrate'] = round(item.get('winrate'), 4) if item.get('winrate') else None
                card_played_list.append(card)
            self.cards_series[faction] = card_played_list
        yield Request(url='https://hsreplay.net/analytics/query/card_included_popularity_report/?GameType=ARENA&TimeRange=LAST_14_DAYS',
                      callback=self.final_parse, dont_filter=True)

    def final_parse(self, response):
        class_faction_dict = {
            'ALL': 'class_all', 'DRUID': 'class_druid', 'HUNTER': 'class_hunter', 'MAGE': 'class_mage',
            'PALADIN': 'class_paladin',
            'PRIEST': 'class_priest', 'ROGUE': 'class_rogue', 'SHAMAN': 'class_shaman', 'WARLOCK': 'class_warlock',
            'WARRIOR': 'class_warrior'
        }
        content = json.loads(response.body).get('series').get('data')
        series = copy.deepcopy(self.cards_series)
        arena_card = HSArenaCardsSpiderItem()
        for card in series['ALL']:
            arena_card['dbfId'] = card['dbfId']
            for faction in series:
                card_played = list(filter(lambda x: x.get('dbfId') == card['dbfId'], series[faction]))
                card_faction_dict = {}
                if len(card_played):
                    temp = {}
                    if card_played[0].get('times_played'): temp['times_played'] = card_played[0].get('times_played')
                    if card_played[0].get('played_pop'): temp['played_pop'] = round(float(card_played[0].get('played_pop')), 4)
                    if card_played[0].get('played_winrate'): temp['played_winrate'] = round(card_played[0].get('played_winrate'), 4)
                    card_faction_dict = temp

                card_included = list(filter(lambda x: x.get('dbf_id') == card['dbfId'], content[faction]))
                if len(card_included) > 0:
                    temp = {}
                    if card_included[0].get('popularity'): temp['deck_pop'] = round(card_included[0].get('popularity'), 4)
                    if card_included[0].get('count'): temp['copies'] = card_included[0].get('count')
                    if card_included[0].get('winrate'): temp['deck_winrate'] = round(card_included[0].get('winrate'), 4)
                    card_faction_dict.update(temp)
                arena_card[class_faction_dict[faction]] = json.dumps(card_faction_dict ,ensure_ascii=False)
            yield arena_card
