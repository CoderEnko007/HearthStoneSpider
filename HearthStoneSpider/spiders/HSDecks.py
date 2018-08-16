# -*- coding: utf-8 -*-
import scrapy
import time
import re
from urllib import parse
from selenium import webdriver
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy import Selector
from scrapy.http import Request

from HearthStoneSpider.items import HSDecksSpiderItem


class HSDecksSpider(scrapy.Spider):
    name = 'HSDecks'
    allowed_domains = ['hsreplay.net/decks']
    start_urls = ['https://hsreplay.net/decks/']

    def __init__(self):
        super(HSDecksSpider, self).__init__()
        chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option("prefs", prefs)  # 无图模式
        # chrome_opt.add_argument('--headless')  # 无页面模式
        self.browser = webdriver.Chrome(executable_path='E:/web_workspace/web_scraper/tools/chromedriver.exe',
                                        chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser

    def spider_closed(self):
        self.browser.close()

    def parse(self, response):
        # page_nums = response.css('div.paging.paging-top ul.pagination li')[-3].css('a::text').extract_first(' ')
        # for i in range(int(page_nums)+1):
        deck_nodes = response.css('div.deck-list>ul>li')[1:]
        for item in deck_nodes:
            temp = item.css('a::attr(href)').extract_first('')
            deck_id = re.match('\/.*\/(.*)\/', temp).group(1)
            faction = item.css('div.deck-tile::attr(data-card-class)').extract_first('')
            deck_name = item.css('div.deck-tile span.deck-name::text').extract_first('')
            dust_cost = item.css('div.deck-tile span.dust-cost::text').extract_first('')
            win_rate = item.css('div.deck-tile span.win-rate::text').extract_first('')
            game_count = item.css('div.deck-tile span.game-count::text').extract_first('')
            duration = item.css('div.deck-tile div.duration::text').extract_first('')
            background_img = re.match('.*url\(\"(https.*)\"\)', item.css('li::attr(style)').extract_first()).group(1)
            url = parse.urljoin(response.url, '/decks/{}'.format(deck_id))
            print(url)
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

        next_page = response.css('div.paging.paging-top ul.pagination li')[-1].css('a::attr(href)').extract_first()
        next_url = 'https://hsreplay.net/decks/{}'.format(next_page)
        yield Request(url=next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        hs_item = HSDecksSpiderItem()
        hs_item['deck_id'] = response.meta.get('deck_id', ' ')
        hs_item['faction'] = response.meta.get('faction', ' ')
        hs_item['deck_name'] = response.meta.get('deck_name', ' ')
        hs_item['dust_cost'] = response.meta.get('dust_cost', ' ')
        hs_item['win_rate'] = response.meta.get('win_rate', ' ')
        hs_item['game_count'] = response.meta.get('game_count', ' ')
        hs_item['duration'] = response.meta.get('duration', ' ')
        hs_item['background_img'] = response.meta.get('background_img', ' ')
        print(response.meta)
        yield hs_item
