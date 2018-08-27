# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals

from HearthStoneSpider.items import HSWinRateSpiderItem
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME


class HSWinRateSpider(scrapy.Spider):
    name = 'HSWinRate'
    allowed_domains = ['hsreplay.net/meta/#tab=archetypes']
    start_urls = ['https://hsreplay.net/meta/#tab=archetypes']

    def __init__(self):
        super(HSWinRateSpider, self).__init__()
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('blink-settings=imagesEnabled=false') # 无图模式
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--headless')  # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser

    def spider_closed(self):
        print('HSWinRate end')
        self.browser.quit()

    def parse(self, response):
        faction_boxes = response.css('div.class-box-container div.box.class-box')
        for box in faction_boxes:
            faction = box.css('div.box-title span.player-class::text').extract_first('')
            archetype_list = box.css('div.grid-container')[2].css('a.player-class::text').extract()
            archetype_list_other_item = box.css('div.grid-container')[2].css('span.player-class div.tooltip-wrapper::text').extract_first('')
            archetype_list.append(archetype_list_other_item)
            data_cells = box.css('div.grid-container')[3].css('.table-cell::text').extract()
            data_list = []
            list = []
            for item in data_cells:
                list.append(item)
                if len(list)%3 == 0:
                    data_list.append(list)
                    list = []
                    continue
            for i, archetype in enumerate(archetype_list):
                hs_item = HSWinRateSpiderItem()
                hs_item['faction'] = faction
                hs_item['archetype'] = archetype
                win_rate = re.findall('\d+', data_list[i][0])
                hs_item['winrate'] = float('.'.join(win_rate))
                popularity = re.findall('\d+', data_list[i][1])
                hs_item['popularity'] = float('.'.join(popularity))
                hs_item['games'] = int(data_list[i][2].replace(',', ''))
                hs_item['date'] = datetime.datetime.now().strftime(SQL_FULL_DATETIME)
                yield hs_item
