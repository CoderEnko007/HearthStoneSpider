# -*- coding: utf-8 -*-
import scrapy
import time
import sys
import os
import json
import copy
import re
import datetime
import platform

from selenium import webdriver
from scrapy import signals
from pydispatch import dispatcher
from scrapy.http import Request
from scrapy.http import HtmlResponse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from HearthStoneSpider.tools.utils import reMatchFormat
from HearthStoneSpider.items import HSDecksSpiderItem
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME, CHANGE_LANGUAGE
from HearthStoneSpider.tools.ifan import iFanr

class BestdeckSpider(scrapy.Spider):
    name = 'BestDeck'
    allowed_domains = ['47.98.187.217']

    def __init__(self, faction=None):
        super(BestdeckSpider, self).__init__()
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--no-sandbox')
        if platform.platform().find('Linux') != -1:
            chrome_opt.add_argument('blink-settings=imagesEnabled=false')  # 无图模式
            chrome_opt.add_argument('--headless')  # 无页面模式
        else:
            chrome_opt.add_argument('blink-settings=imagesEnabled=false')  # 无图模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)
        # dispatcher.connect(self.item_scraped, signals.item_scraped)
        self.ifanr = iFanr()
        self.langToggleClicked = False
        self.addCookieFlag = True
        self.faction = eval(faction) if faction else None

    def start_requests(self):
        url = 'http://47.98.187.217/winrate/?rank_range=BRONZE_THROUGH_GOLD&format=json&create_time={0}'.format(time.strftime("%Y-%m-%d", time.localtime()))
        yield Request(url, dont_filter=True)

    def spider_closed(self):
        print('BestDeck end')
        self.browser.quit()

    def engine_stopped(self):
        print('BestDeck engine end')

    def parse(self, response):
        content = json.loads(response.body)
        next_url = content.get('next')
        results = content.get('results')
        for item in results[:2]:
            # if item['archetype'].lower() != 'HIGHLANDER HUNTER'.lower():
            #     continue
            faction = item['faction']['id']
            self.faction = [faction.lower() for faction in self.faction] if self.faction else None
            if self.faction and faction.lower() not in self.faction:
                continue
            if (item['archetype'] != 'Other'):
                faction = item['faction']['id']
                deck_name = item['archetype']
                best_deck = json.loads(item['best_deck'])
                if len(best_deck)<=0:
                    continue
                deck_id = best_deck[0]
                winrate = best_deck[1]
                games = best_deck[2]
                deck_url = 'https://hsreplay.net/decks/{0}/#rankRange=DIAMOND_THROUGH_LEGEND&tab=overview'.format(deck_id)
                yield Request(url=deck_url, meta={
                    'deck_id': deck_id,
                    'faction': faction,
                    'deck_name': deck_name,
                    'games': games,
                }, callback=self.parse_deck, dont_filter=True)
        if next_url:
            yield Request(url=next_url, callback=self.parse, dont_filter=True)

    def parse_deck(self, response):
        meta = copy.copy(response.meta)
        hs_item = HSDecksSpiderItem()
        hs_item['deck_id'] = meta.get('deck_id', '')
        hs_item['faction'] = meta.get('faction', '')
        hs_item['deck_name'] = meta.get('deck_name', '')
        # hs_item['win_rate'] = float(meta.get('win_rate', ''))
        # hs_item['game_count'] = int(meta.get('game_count', ''))
        # hs_item['duration'] = float(meta.get('duration', ''))
        hs_item['background_img'] = ''
        hs_item['trending_flag'] = False
        hs_item['mode'] = 'Standard'
        hs_item['last_30_days'] = False

        if CHANGE_LANGUAGE and not self.langToggleClicked and platform.platform().find('Windows') != -1:
            langToggle = self.browser.find_elements_by_css_selector('.dropdown-toggle')[0]
            langToggle.click()
            langItemEn = self.browser.find_elements_by_css_selector('.dropdown-menu li')[0]
            langItemEn.click()
            overviewBtn = self.browser.find_elements_by_css_selector('#tab-overview')[0]
            overviewBtn.click()
            time.sleep(3)
            self.langToggleClicked = True
            response = HtmlResponse(
                url=self.browser.current_url,
                body=self.browser.page_source,
                encoding='utf-8',
            )

        deck_info = response.css('.infobox ul li span.infobox-value::text').extract()
        if len(deck_info)>0:
            dust_cost = deck_info[0].split(' ')[0]
        hs_item['dust_cost'] = dust_cost if len(deck_info) else ''

        deck_data = response.css('.infobox section ul span.infobox-value::text').extract()
        if len(deck_data) > 0:
            print('aaaaa:', deck_data)
            for item in deck_data:
                t = item.replace(',', '').split(' ')
                game_count_item = t[0] if 'games' in t else ''
            print('bbbbb:', game_count_item)
            real_game_count = int(game_count_item) if game_count_item.isdigit() else ''
            hs_item['real_game_count'] = real_game_count
        else:
            hs_item['real_game_count'] = ''

        card_list_items = response.css('#overview .card-list-wrapper .card-list .tooltip-wrapper .card-tile')
        card_list = []
        for item in card_list_items:
            card_cost = int(item.css('span.card-cost::text').extract_first(''))
            card_asset = item.css('div.card-frame img.card-asset::attr(src)').extract_first('')
            card_hsid = card_asset.split('/')[-1].split('.')[0]
            card_count = item.css('.card-count::text').extract_first('')
            card_count = int(card_count) if card_count.isdigit() else 1
            card_name = item.css('.card-name::text').extract_first('')
            card_list.append({'name': card_name, 'cost': card_cost, 'count': card_count, 'card_hsid': card_hsid})
        hs_item['card_list'] = card_list

        striped_trs = response.css('table.table-striped tbody tr')
        duration = striped_trs[0].css('td:nth-of-type(2)::text').extract_first('') if len(striped_trs)>0 else ''
        hs_item['duration'] = float(duration.split(' ')[0]) if ' ' in duration else None

        turns = striped_trs[1].css('td:nth-of-type(2)::text').extract_first('') if len(striped_trs)>1 else ''
        hs_item['turns'] = float(turns) if turns != '' else None

        winrate = striped_trs[3].css('td:nth-of-type(2)::text').extract_first('') if len(striped_trs)>3 else ''
        hs_item['win_rate'] = float(winrate.replace('%', '')) if winrate != '' else None
        hs_item['real_win_rate'] = hs_item['win_rate']

        # turns_field = response.css('table.table-striped tbody tr')
        # turns = turns_field[1].css('td::text').extract() if len(turns_field) > 1 else []
        # hs_item['turns'] = float(turns[1]) if len(turns) > 1 else ''

        # win_rate_cell = response.css('table.table-striped tbody tr td.winrate-cell::text').extract()
        # if win_rate_cell:
        #     win_rate_cell = win_rate_cell[0].replace('%', '')
        #     hs_item['real_win_rate'] = float(win_rate_cell)
        # else:
        #     print('win_rate_cell', win_rate_cell)
        #     hs_item['real_win_rate'] = hs_item['win_rate']
        #     print('BestDeck.py hs_item:', hs_item)
        # print('test win_rate', hs_item['deck_id'], hs_item['win_rate'], hs_item['real_win_rate'])

        win_rate_nodes = response.css('table.table-striped tbody tr')
        faction_win_rate = []
        for item in win_rate_nodes[4:]:
            faction_str = item.css('td span.player-class::attr(class)').extract_first('')
            faction = reMatchFormat('.* (\w*)$', faction_str.strip()).capitalize()
            if faction == 'Demonhunter':
                faction = 'DemonHunter'
            win_rate = item.css('td.winrate-cell::text').extract_first('')
            win_rate = re.findall('\d+', win_rate)
            win_rate = '.'.join(win_rate)
            faction_win_rate.append({'faction': faction, 'win_rate': win_rate})
        hs_item['faction_win_rate'] = json.dumps(faction_win_rate)
        hs_item['date'] = datetime.datetime.now().strftime(SQL_FULL_DATETIME)

        # url = 'https://hsreplay.net/analytics/query/single_deck_mulligan_guide'
        # params = {
        #     'GameType': 'RANKED_STANDARD',
        #     'RankRange': 'ALL',
        #     'Region': 'ALL',
        #     'PlayerInitiative': 'ALL',
        #     'deck_id': hs_item['deck_id']
        # }
        # header = {
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        # res = requests.get(url=url, params=params, headers=header)
        # re_dict = json.loads(res.text)
        # hs_item['mulligan'] = re_dict['series']['data']['ALL']
        # yield hs_item
        url = 'https://hsreplay.net/analytics/query/single_deck_mulligan_guide_v2/?GameType=RANKED_STANDARD&RankRange=DIAMOND_THROUGH_LEGEND&Region=ALL&PlayerInitiative=ALL&deck_id=' + \
              hs_item['deck_id']
        yield Request(url=url, callback=self.parse_mulligan, meta={'data': hs_item}, dont_filter=True)
        # yield hs_item

    def parse_mulligan(self, response):
        meta = response.meta
        hs_item = meta.get('data')
        res_data = response.css('pre::text').extract_first('')
        if res_data and res_data != '':
            json_data = json.loads(res_data)
            hs_item['mulligan'] = json_data['series']['data']['ALL']
        else:
            hs_item['mulligan'] = ''
        yield hs_item