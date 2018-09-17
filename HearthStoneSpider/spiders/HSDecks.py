# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
from urllib import parse
from selenium import webdriver
from scrapy import signals
from pydispatch import dispatcher
from scrapy.http import Request
# import pyperclip

from HearthStoneSpider.items import HSDecksSpiderItem
from HearthStoneSpider.tools.utils import reMatchFormat
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME


class HSDecksSpider(scrapy.Spider):
    name = 'HSDecks'
    allowed_domains = ['hsreplay.net/decks']
    start_urls = ['https://hsreplay.net/decks/']

    def __init__(self):
        super(HSDecksSpider, self).__init__()
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('blink-settings=imagesEnabled=false') # 无图模式
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--headless')  # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser

    def spider_closed(self):
        print('HSDecks end')
        self.browser.quit()

    def parse(self, response):
        deck_nodes = response.css('div.deck-list>ul>li')[1:]
        # deck_nodes = response.css('div.deck-list>ul>li')[-2:]
        for item in deck_nodes:
            deck_id = item.css('a::attr(href)').extract_first('')
            deck_id = reMatchFormat('\/.*\/(.*)\/', deck_id.strip())
            faction = item.css('div.deck-tile::attr(data-card-class)').extract_first('').capitalize()
            deck_name = item.css('div.deck-tile span.deck-name::text').extract_first('')
            dust_cost = item.css('div.deck-tile span.dust-cost::text').extract_first('')
            win_rate = item.css('div.deck-tile span.win-rate::text').extract_first('')
            win_rate = re.findall('\d+', win_rate)
            win_rate = '.'.join(win_rate)
            game_count = item.css('div.deck-tile span.game-count::text').extract_first('')
            game_count = game_count.replace(',', '')
            duration = item.css('div.deck-tile div.duration::text').extract_first('')
            duration = reMatchFormat('.*?(\d*\.?\d*).*', duration.strip())
            background_img = item.css('li::attr(style)').extract_first('')
            background_img = reMatchFormat('.*url\(\"(https.*)\"\)', background_img)
            url = parse.urljoin(response.url, '/decks/{}'.format(deck_id))
            yield Request(url=url, meta={
                'deck_id': deck_id,
                'faction': faction,
                'deck_name': deck_name,
                'dust_cost': dust_cost,
                'win_rate': win_rate,
                'game_count': game_count,
                'duration': duration,
                'background_img': background_img
            }, callback=self.parse_detail, dont_filter=True)

        page = response.css('div.paging.paging-top ul.pagination li')
        if len(page)>0:
            next_href = page[-1].css('a::attr(href)').extract_first()
            next_url = 'https://hsreplay.net/decks/{}'.format(next_href)
            yield Request(url=next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        hs_item = HSDecksSpiderItem()
        hs_item['deck_id'] = response.meta.get('deck_id', ' ')
        hs_item['faction'] = response.meta.get('faction', ' ')
        hs_item['deck_name'] = response.meta.get('deck_name', ' ')
        hs_item['dust_cost'] = int(response.meta.get('dust_cost', ' '))
        hs_item['win_rate'] = float(response.meta.get('win_rate', ' '))
        hs_item['game_count'] = int(response.meta.get('game_count', ' '))
        hs_item['duration'] = float(response.meta.get('duration', ' '))
        hs_item['background_img'] = response.meta.get('background_img', ' ')

        card_list_items = response.css('#overview div.card-list-wrapper ul.card-list div.tooltip-wrapper div.card-tile')
        card_list = []
        for item in card_list_items:
            card_cost = item.css('span.card-cost::text').extract_first('')
            card_asset = item.css('div.card-frame img.card-asset::attr(src)').extract_first('')
            card_count = item.css('span.card-count::text').extract_first('')
            # card_count = re.findall('\d+', card_count)
            card_name = item.css('span.card-name::text').extract_first('')
            card_list.append({'name': card_name, 'cost': card_cost, 'count': card_count, 'img': card_asset})
        hs_item['card_list'] = card_list

        turns_field = response.css('table.table-striped tbody tr')
        turns = turns_field[1].css('td::text').extract() if len(turns_field)>1 else []
        hs_item['turns'] = float(turns[1]) if len(turns)>1 else '0'
        win_rate_nodes = response.css('table.table-striped tbody tr')
        faction_win_rate = []
        for item in win_rate_nodes[4:]:
            faction_str = item.css('td span.player-class::attr(class)').extract_first('')
            faction = reMatchFormat('.* (\w*)$', faction_str.strip()).capitalize()
            win_rate = item.css('td.winrate-cell::text').extract_first('')
            win_rate = re.findall('\d+', win_rate)
            win_rate = '.'.join(win_rate)
            faction_win_rate.append({'faction': faction, 'win_rate': win_rate})
        hs_item['faction_win_rate'] = json.dumps(faction_win_rate, indent=4)
        hs_item['date'] = datetime.datetime.now().strftime(SQL_FULL_DATETIME)
        yield hs_item
