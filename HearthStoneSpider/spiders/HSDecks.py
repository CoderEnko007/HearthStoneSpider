# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
import copy
import sys
import os
from urllib import parse
from selenium import webdriver
from scrapy import signals
from pydispatch import dispatcher
from scrapy.http import Request
from scrapy.cmdline import execute


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from HearthStoneSpider.items import HSDecksSpiderItem
from HearthStoneSpider.tools.utils import reMatchFormat
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME
from HearthStoneSpider.tools.ifan import iFanr


class HSDecksSpider(scrapy.Spider):
    name = 'HSDecks'
    # allowed_domains = ['hsreplay.net/decks/']
    # start_urls = ['https://hsreplay.net/decks/#minGames=400',
    #               'https://hsreplay.net/decks/trending/']
    # start_urls = ['https://hsreplay.net/decks/trending/']
    # start_urls = ['https://hsreplay.net/decks/',
    #               'https://hsreplay.net/decks/trending/']
    # start_urls = ['https://hsreplay.net/decks/#timeRange=LAST_30_DAYS']
    start_urls = ['https://hsreplay.net/decks/']
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True)

    def __init__(self, params=None):
        super(HSDecksSpider, self).__init__()
        if params == 'trending':
            self.start_urls = ['https://hsreplay.net/decks/trending/']
        elif params == 'interrupt':
            self.start_urls = ['https://hsreplay.net/decks/#page=71']
        else:
            self.start_urls = ['https://hsreplay.net/decks/']
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('blink-settings=imagesEnabled=false') # 无图模式
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--headless')  # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)
        # dispatcher.connect(self.item_scraped, signals.item_scraped)
        self.ifanr = iFanr()
        self.interrupt_page = 70
        print('测试中断 params=',params)
        self.current_page = self.interrupt_page+1 if params == 'interrupt' else 1 # 70页需要关闭chrome重新开启
        self.total_page = 0

    def spider_closed(self):
        print('HSDecks end')
        self.browser.quit()

    def engine_stopped(self):
        print('HSDecks engine end')
        # requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/z1s4JcQZcx')
        # if self.current_page==self.interrupt_page:
        #     execute(['scrapy', 'crawl', 'HSDecks', '-a', "params=interrupt"])

    def item_scraped(self, response, spider):
        print('item_scraped end')

    def parse(self, response):
        trending_flag = False
        mode = 'Standard' # 这里只爬取标准模式卡组
        last_30_days = True # 默认是最近30天的卡组
        if response.url.find('trending')>0:
            deck_nodes = response.css('.deck-list>ul>li')
            trending_flag = True
        else:
            if response.url.find('LAST_30_DAYS')>0:
                last_30_days = True
            else:
                last_30_days = False
            deck_nodes = response.css('.deck-list>ul>li')[1:]

        # deck_nodes = response.css('div.deck-list>ul>li')[-2:]
        for item in deck_nodes:
            deck_id = item.css('a::attr(href)').extract_first('')
            deck_id = reMatchFormat('\/.*\/(.*)\/', deck_id.strip())
            faction = item.css('.deck-tile::attr(data-card-class)').extract_first('').capitalize()
            deck_name = item.css('.deck-tile .deck-name::text').extract_first('')
            dust_cost = item.css('.deck-tile .dust-cost::text').extract_first('')
            win_rate = item.css('.deck-tile .win-rate::text').extract_first('')
            win_rate = re.findall('\d+', win_rate)
            win_rate = '.'.join(win_rate)
            game_count = item.css('.deck-tile .game-count::text').extract_first('')
            game_count = game_count.replace(',', '')
            duration = item.css('.deck-tile .duration::text').extract_first('')
            duration = reMatchFormat('.*?(\d*\.?\d*).*', duration.strip())
            background_img = item.css('li::attr(style)').extract_first('')
            background_img = reMatchFormat('.*url\(\"(https.*)\"\)', background_img)
            url = parse.urljoin(response.url, '/decks/{}/#tab=overview'.format(deck_id))
            yield Request(url=url, meta={
                'deck_id': deck_id,
                'faction': faction,
                'deck_name': deck_name,
                'dust_cost': dust_cost,
                'win_rate': win_rate,
                'game_count': game_count,
                'duration': duration,
                'background_img': background_img,
                'trending_flag': trending_flag,
                'mode': mode,
                'last_30_days': last_30_days
            }, callback=self.parse_detail, dont_filter=True)

        if not trending_flag:
            total_page = response.css('div.paging.paging-top ul.pagination li.hidden-lg span::text').extract_first('')
            if total_page and self.total_page==0:
                self.total_page = int(re.match('.*\/ ?(\d*)', total_page).group(1))
                print('yf_log total_page:', self.total_page)
            if self.total_page > 0:
                self.current_page += 1
                # 爬取一半需要重启webdriver
                if self.current_page == self.interrupt_page:
                    print('已经爬取了%s页,暂时停止爬虫'%self.interrupt_page)
                    return
                if self.current_page <= self.total_page:
                    if last_30_days:
                        next_url = 'https://hsreplay.net/decks/#timeRange=LAST_30_DAYS&page={}'.format(self.current_page)
                    else:
                        next_url = 'https://hsreplay.net/decks/#page={}'.format(self.current_page)
                    print('yf_log next_url', next_url)
                    yield Request(url=next_url, callback=self.parse, dont_filter=True)
            # page = response.css('div.paging.paging-top ul.pagination li')
            # if len(page)>0:
            #     next_href = page[-1].css('a::attr(href)').extract_first()
            #     if next_href:
            #         next_url = 'https://hsreplay.net/decks/#timeRange=LAST_30_DAYS{}'.format(next_href.replace('#', '&'))
            #         print('yf_log', next_url)
            #         yield Request(url=next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        meta = copy.copy(response.meta)
        hs_item = HSDecksSpiderItem()
        hs_item['deck_id'] = meta.get('deck_id', '')
        hs_item['faction'] = meta.get('faction', '')
        hs_item['deck_name'] = meta.get('deck_name', '')
        hs_item['dust_cost'] = meta.get('dust_cost', '')
        hs_item['win_rate'] = float(meta.get('win_rate', ''))
        hs_item['game_count'] = int(meta.get('game_count', ''))
        hs_item['duration'] = float(meta.get('duration', ''))
        hs_item['background_img'] = meta.get('background_img', '')
        hs_item['trending_flag'] = meta.get('trending_flag', '')
        hs_item['mode'] = meta.get('mode', '')
        hs_item['last_30_days'] = meta.get('last_30_days', '')

        real_game_count = response.css('.infobox section ul span.infobox-value').extract()
        if real_game_count:
            real_game_count = real_game_count[0].replace(',', '')
            hs_item['real_game_count'] = int(re.findall('\d+', real_game_count)[0])
        else:
            hs_item['real_game_count'] = hs_item['game_count']

        card_list_items = response.css('#overview div.card-list-wrapper ul.card-list div.tooltip-wrapper div.card-tile')
        card_list = []
        for item in card_list_items:
            card_cost = int(item.css('span.card-cost::text').extract_first(''))
            card_asset = item.css('div.card-frame img.card-asset::attr(src)').extract_first('')
            card_hsid = card_asset.split('/')[-1].split('.')[0]
            card_count = item.css('span.card-count::text').extract_first('')
            card_count = int(card_count) if card_count.isdigit() else 1
            # card_count = re.findall('\d+', card_count)
            card_name = item.css('span.card-name::text').extract_first('')
            card_list.append({'name': card_name, 'cost': card_cost, 'count': card_count, 'card_hsid': card_hsid})
        hs_item['card_list'] = card_list

        turns_field = response.css('table.table-striped tbody tr')
        turns = turns_field[1].css('td::text').extract() if len(turns_field)>1 else []
        hs_item['turns'] = float(turns[1]) if len(turns)>1 else ''

        win_rate_cell = response.css('table.table-striped tbody tr td.winrate-cell::text').extract()
        if win_rate_cell:
            win_rate_cell = win_rate_cell[0].replace('%', '')
            hs_item['real_win_rate'] = float(win_rate_cell)
        else:
            print('win_rate_cell', win_rate_cell)
            hs_item['real_win_rate'] = hs_item['win_rate']
            print('hs_item:', hs_item)
        # try:
        #     hs_item['real_win_rate'] = float(win_rate_cell)
        # except Exception as e:
        #     hs_item['real_win_rate'] = ''
        #     print(e)
        #     print('win_rate_cell:', win_rate_cell)
        #     print('hs_item:', hs_item)
        print('test win_rate', hs_item['deck_id'], hs_item['win_rate'], hs_item['real_win_rate'])

        win_rate_nodes = response.css('table.table-striped tbody tr')
        faction_win_rate = []
        for item in win_rate_nodes[4:]:
            faction_str = item.css('td span.player-class::attr(class)').extract_first('')
            faction = reMatchFormat('.* (\w*)$', faction_str.strip()).capitalize()
            win_rate = item.css('td.winrate-cell::text').extract_first('')
            win_rate = re.findall('\d+', win_rate)
            win_rate = '.'.join(win_rate)
            faction_win_rate.append({'faction': faction, 'win_rate': win_rate})
        hs_item['faction_win_rate'] = json.dumps(faction_win_rate)
        hs_item['date'] = datetime.datetime.now().strftime(SQL_FULL_DATETIME)

        self.crawler.stats.inc_value('decks_scraped')
        yield hs_item
