# -*- coding: utf-8 -*-
import scrapy
import json
from datetime import datetime

from scrapy import signals
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
    start_urls = ['https://hsreplay.net/analytics/query/card_played_popularity_report/?GameType=ARENA&timeRange=LAST_14_DAYS']

    def __init__(self, params=None):
        super(HSArenaCardsSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser
        self.ifanr = iFanr()
        self.total_count = 0
        self.scraped_count = 0
        self.temp_count = 0
        self.cards_series = {}
        self.extra_data_flag = True if params=='extra_data' else False

    def spider_closed(self):
        now = datetime.now().strftime(SQL_FULL_DATETIME)
        # db = DBManager()
        # fc = db.select('cards_arenacards', cols="name, dbfId, hsId, cardClass, classification, ename, "
        #                                         "deck_pop, copies, deck_winrate, times_played, played_pop, played_winrate", today=True)
        # filename ="{}/{}_arena_json_file.json".format(ARENA_FILES, datetime.now().strftime('%Y%m%d_%H%M%S'))
        # json_str = json.dumps({'data': fc}, indent=4, ensure_ascii=False, cls=DecimalEncoder)
        # with open(filename, 'w', encoding='utf-8') as json_file:
        #     json_file.write(json_str)
        #
        # self.ifanr.import_table_data(tableID=self.ifanr.tablesID['arena_cards'], filename=filename)
        # res = self.ifanr.get_table_data(tableID=iFanr.tablesID['table_config'])
        # if res:
        #     if (res.get('meta').get('total_count') and res.get('objects')):
        #         arena_config = res.get('objects')[0]
        #         id = arena_config['id']
        #         backup_table = arena_config['arena_table_backup']
        #         online_table = arena_config['arena_table_online']
        #         self.ifanr.import_table_data(tableID=backup_table, filename=filename)
        # else:
        #     print('yf_log res is none')
        #
        print('{0}:HSArenaCards end'.format(now))


    def parse(self, response):
        content = json.loads(response.body).get('series').get('data')
        for faction in content:
            self.total_count += len(content[faction])
        for faction in content:
        # faction = 'ALL'
            card_played_list = []
            for item in content[faction]:
                card = HSArenaCardsSpiderItem()
                card['classification'] = faction
                card['dbfId'] = item.get('dbf_id')
                card['times_played'] = item.get('total') if item.get('total') else None
                card['played_pop'] = round(float(item.get('popularity')), 4) if item.get('popularity') else None
                card['played_winrate'] = round(item.get('winrate'), 4) if item.get('winrate') else None
                card_played_list.append(card)
            self.cards_series[faction] = card_played_list
        yield Request(url='https://hsreplay.net/analytics/query/card_included_popularity_report/?GameType=ARENA&timeRange=LAST_14_DAYS',
                      callback=self.final_parse, dont_filter=True)

    def final_parse(self, response):
        content = json.loads(response.body).get('series').get('data')
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
