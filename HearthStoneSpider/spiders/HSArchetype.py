# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals
from urllib import parse
from scrapy.http import Request

from HearthStoneSpider.items import HSArchetypeSpiderItem


class HSArchetypeSpider(scrapy.Spider):
    name = 'HSArchetype'
    allowed_domains = ['hsreplay.net/meta']
    start_urls = ['http://hsreplay.net/meta/']

    def __init__(self):
        super(HSArchetypeSpider, self).__init__()
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('blink-settings=imagesEnabled=false') # 无图模式
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--headless')  # 无页面模式
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser

    def spider_closed(self):
        self.browser.close()

    def parse(self, response):
        archetype_tier = response.css('div.archetype-tier-list div.tier')
        for item in archetype_tier:
            tier = item.css('div.tier-header::text').extract_first('')
            archetype_list_items = item.css('li.archetype-list-item')
            for arche in archetype_list_items:
                archetype_name = arche.css('div.archetype-name::text').extract_first('')
                faction = archetype_name.split(' ')[-1]
                win_rate = arche.css('div.archetype-data::text').extract_first('')
                detail_url = arche.css('a::attr(href)')[0].extract()
                detail_url = parse.urljoin(response.url, detail_url)
                yield Request(url=detail_url, meta={
                    'tier': tier,
                    'faction': faction,
                    'archetype_name': archetype_name,
                    'win_rate': win_rate
                }, callback=self.parse_detail, dont_filter=True)

    def parse_detail(self, response):
        win_rate = response.css('a.winrate-box .box-content h1::text').extract_first('')
        popularity = response.css('a.popularity-box .box-content h1::text').extract_first('')
        best_matchup_player_class = response.css('a.matchup-box')[0].css('span.player-class::text').extract_first('')
        best_matchup_win_rate = response.css('a.matchup-box')[0].css('div.stats-table tr')[0].css('td::text').extract_first('')
        best_matchup_games = response.css('a.matchup-box')[0].css('div.stats-table tr')[1].css('td::text').extract_first('')
        best_matchup = [best_matchup_player_class, best_matchup_win_rate, best_matchup_games]
        worst_matchup_player_class = response.css('a.matchup-box')[1].css('span.player-class::text').extract_first('')
        worst_matchup_win_rate = response.css('a.matchup-box')[1].css('div.stats-table tr')[0].css('td::text').extract_first('')
        worst_matchup_games = response.css('a.matchup-box')[1].css('div.stats-table tr')[1].css('td::text').extract_first('')
        worst_matchup = [worst_matchup_player_class, worst_matchup_win_rate, worst_matchup_games]

        card_list_wrapper = response.css('div.archetype-signature div.card-list-wrapper')
        core_card_list_items = card_list_wrapper[0].css('div.card-tile') if card_list_wrapper is not None else []
        core_cards = []
        for item in core_card_list_items:
            card_name = item.css('span.card-name::text').extract_first('')
            card_cost = item.css('span.card-cost::text').extract_first('')
            card_assert = item.css('img.card-asset::attr(src)').extract_first('')
            core_cards.append([card_name, card_cost, card_assert])

        pop_card_list_items = card_list_wrapper[1].css('div.card-tile') if len(card_list_wrapper)>=2 else []
        pop_cards = []
        for item in pop_card_list_items:
            card_name = item.css('span.card-name::text').extract_first('')
            card_cost = item.css('span.card-cost::text').extract_first('')
            card_assert = item.css('img.card-asset::attr(src)').extract_first('')
            pop_cards.append([card_name, card_cost, card_assert])
        print(response.url)

        matchup_url = response.css('a#tab-matchups::attr(href)').extract_first('')
        url = parse.urljoin(response.url, matchup_url)
        yield Request(url=url, meta={
            'tier_meta': response.meta,
            'win_rate': win_rate,
            'popularity': popularity,
            'best_matchup': best_matchup,
            'worst_matchup': worst_matchup,
            'core_cards': core_cards,
            'pop_cards': pop_cards,
        }, callback=self.matchup_detail, dont_filter=True)
        
    def matchup_detail(self, response):
        hs_item = HSArchetypeSpiderItem()
        hs_item['tier'] = response.meta.get('tier_meta').get('tier')
        hs_item['faction'] = response.meta.get('tier_meta').get('faction')
        hs_item['archetype_name'] = response.meta.get('tier_meta').get('archetype_name')
        # hs_item['win_rate'] = response.meta.tier_meta.get('win_rate')
        hs_item['win_rate'] = response.meta.get('win_rate')
        hs_item['popularity'] = response.meta.get('popularity')
        hs_item['best_matchup'] = response.meta.get('best_matchup')
        hs_item['worst_matchup'] = response.meta.get('worst_matchup')
        hs_item['core_cards'] = response.meta.get('core_cards')
        hs_item['pop_cards'] = response.meta.get('pop_cards')
        print(hs_item)

        faction_boxes = response.css('div.class-box-container div.box.class-box')
        matchup = []
        for box in faction_boxes:
            faction = box.css('div.box-title span.player-class::text').extract_first('')
            archetype_list = box.css('div.grid-container')[2].css('a.player-class::text').extract()
            data_cells = box.css('div.grid-container')[3].css('a.table-cell::text').extract()
            data_list = []
            list = []
            for item in data_cells:
                list.append(item)
                if len(list) % 3 == 0:
                    data_list.append(list)
                    list = []
                    continue
            for i, archetype in enumerate(archetype_list):
                data_list[i].insert(0, archetype)
            matchup.append(data_list)
        hs_item['matchup'] = matchup
        yield hs_item
