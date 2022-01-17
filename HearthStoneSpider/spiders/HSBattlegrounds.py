# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import numpy as np
from datetime import datetime
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals
from scrapy.http import Request
from HearthStoneSpider.settings import SQL_FULL_DATETIME
from HearthStoneSpider.items import BattlegroundsSpiderItem


class HSBattlegroundsSpider(scrapy.Spider):
    name = 'HSBattlegrounds'
    allowed_domains = ['hsreplay.net/']
    start_urls = ['https://hsreplay.net/analytics/query/battlegrounds_data_volume_manifest/']

    def __init__(self, local_update=False):
        super(HSBattlegroundsSpider, self).__init__()
        self.local_update = eval(local_update)
        self.mmrRange = 'TOP_50_PERCENT'
        self.timeRange = 'LAST_7_DAYS'
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('blink-settings=imagesEnabled=false')  # 无图模式
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--no-sandbox')
        # chrome_opt.add_argument('--headless')  # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)
        # self.addCookieFlag = True
        self.total_games = 0
        self.min_mmr = 0
        self.std = 0
        self.bg_items_list = []

    def spider_closed(self):
        print('HSBattlegroundsSpider end')
        self.browser.quit()

    def engine_stopped(self):
        print('HSBattlegroundsSpider engine end')
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/qX9Oup6OdW/') # battlegrounds_tier_list

    def parse(self, response):
        if self.local_update:
            jsonData = '{"render_as":"table","series":{"metadata":{"CURRENT_BATTLEGROUNDS_PATCH":{"min_mmr":{"ALL":434.0,"TOP_20_PERCENT":6741.0,"TOP_50_PERCENT":6094.0,"TOP_5_PERCENT":7687.0,"TOP_1_PERCENT":9920.0},"total_games":6862716},"LAST_7_DAYS":{"min_mmr":{"ALL":434.0,"TOP_50_PERCENT":6094.0,"TOP_20_PERCENT":6741.0,"TOP_5_PERCENT":7687.0,"TOP_1_PERCENT":9920.0},"total_games":4026019},"current_battlegrounds_patch_date":"2021-07-02"},"data":[]},"as_of":"2021-07-13T01:53:16Z"}'
        else:
            jsonData = response.css('pre::text').extract_first('')
        content = json.loads(jsonData).get('series').get('metadata')
        self.total_games = content.get(self.timeRange).get('total_games')
        self.min_mmr = content.get(self.timeRange).get('min_mmr').get(self.mmrRange)

        # https://hsreplay.net/analytics/query/battlegrounds_list_heroes/?BattlegroundsMMRPercentile=TOP_50_PERCENT&BattlegroundsTimeRange=LAST_7_DAYS
        url = 'https://hsreplay.net/analytics/query/battlegrounds_list_heroes/?BattlegroundsMMRPercentile={}&BattlegroundsTimeRange={}'\
            .format(self.mmrRange, self.timeRange)
        yield Request(url=url, callback=self.json_parse, dont_filter=True)

    def json_parse(self, response):
        jsonData = response.css('pre::text').extract_first('')
        content = json.loads(jsonData).get('series').get('data')
        # 以4.5为分界，分别计算标准差
        avg_rang_list1 = [x.get('avg_final_placement') for x in content if x.get('avg_final_placement') < 4.5]
        avg_rang_list2 = [x.get('avg_final_placement') for x in content if x.get('avg_final_placement') >= 4.5]
        stddev1 = round(np.std(avg_rang_list1, ddof=1), 2)
        stddev2 = round(np.std(avg_rang_list2, ddof=1), 2)
        min_avg_rank1 = round(np.min(avg_rang_list1), 2)
        avg1 = round(np.mean(avg_rang_list1), 2)
        min_avg_rank2 = round(np.min(avg_rang_list2), 2)
        avg2 = round(np.mean(avg_rang_list2), 2)
        print('1. 标准差：{}, 最小值：{}, 平均值：{}'.format(stddev1, min_avg_rank1, avg1))
        print('2. 标准差：{}, 最小值：{}, 平均值：{}'.format(stddev2, min_avg_rank2, avg2))
        for item in content:
            bg_item = BattlegroundsSpiderItem()
            bg_item['mmr_range'] = self.mmrRange
            bg_item['min_mmr'] = int(self.min_mmr)
            bg_item['time_frame'] = self.timeRange
            bg_item['total_games'] = self.total_games/2 if self.mmrRange == 'TOP_50_PERCENT' else self.total_games
            bg_item['dbf_id'] = item.get('hero_dbf_id')
            bg_item['num_games_played'] = item.get('num_games_played')
            bg_item['pick_rate'] = item.get('pick_rate')
            bg_item['popularity'] = item.get('popularity')
            bg_item['times_offered'] = item.get('times_offered')
            bg_item['times_chosen'] = item.get('times_chosen')
            bg_item['avg_final_placement'] = round(item.get('avg_final_placement'), 2)
            bg_item['final_placement_distribution'] = str(item.get('final_placement_distribution'))
            bg_item['update_time'] = datetime.now().strftime(SQL_FULL_DATETIME)
            if bg_item['avg_final_placement']<min_avg_rank1+stddev1:
                bg_item['tier'] = 'T1'
            elif bg_item['avg_final_placement']>=min_avg_rank1+stddev1 and bg_item['avg_final_placement']<4.5:
                bg_item['tier'] = 'T2'
            elif bg_item['avg_final_placement']>=4.5 and bg_item['avg_final_placement']<min_avg_rank2+stddev2:
                bg_item['tier'] = 'T3'
            elif bg_item['avg_final_placement']>=min_avg_rank2+stddev2:
                bg_item['tier'] = 'T4'
            # self.bg_items_list.append(bg_item)
            print(bg_item['dbf_id'], bg_item['tier'])
            yield bg_item
        # yield Request(url='https://hsreplay.net/battlegrounds/heroes/', callback=self.tier_parse, dont_filter=True)

    def tier_parse(self, response):
        bgs_table_row = response.css('.ReactVirtualized__Grid__innerScrollContainer .bgs-table__row-container')
        tier_list = {'Tier 1':[], 'Tier 2':[], 'Tier 3':[], 'Tier 4':[]}
        tier_str = ''
        for row in bgs_table_row:
            row_tier = row.css('.bgs-table__row .row-info-tier')
            row_hero = row.css('.bgs-table__row .bgs-table-cell__hero')
            if len(row_tier)>0:
                text = row_tier.css('.sr-only strong::text').extract_first('')
                tier_str = text
            elif len(row_hero)>0:
                text = row_hero.css('.bgs-table-cell__hero-right span::text').extract_first('')
                tier_list[tier_str].append(text)
        for item in self.bg_items_list:
            print(item)
        pass