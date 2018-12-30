# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
import json
import requests
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals
from urllib import parse
from scrapy.http import Request

from HearthStoneSpider.items import HSArchetypeSpiderItem
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME


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
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)

    def spider_closed(self):
        print('HSArchetype end')
        self.browser.quit()

    def engine_stopped(self):
        print('HSArchetype engine end')
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/UJ15lz8GSk')

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
        # win_rate = response.css('a.winrate-box .box-content h1::text').extract_first('')
        # win_rate = re.findall('\d+', win_rate)
        # win_rate = '.'.join(win_rate)
        game_count = response.css('a.winrate-box .box-content h3::text').extract_first('')
        game_count = re.findall('\d+', game_count)
        game_count = ''.join(game_count)
        popularity = response.css('a.popularity-box .box-content h1::text').extract_first('')
        popularity = re.findall('\d+', popularity)
        popularity = '.'.join(popularity)

        deck_box = response.css('a.deck-box')
        if len(deck_box)>0 and len(response.css('a.deck-box::attr(href)'))>0:
            pop_deck_code = response.css('a.deck-box::attr(href)')[0].extract()
            pop_deck_code = re.match('.*\/(.*)\/', pop_deck_code).group(1)
            pop_deck_win_rate = deck_box[0].css('div.stats-table tr')[0].css('td::text').extract_first('')
            pop_deck_games = deck_box[0].css('div.stats-table tr')[1].css('td::text').extract_first('')
            pop_deck = [pop_deck_code, pop_deck_win_rate, pop_deck_games]
        else:
            pop_deck = []
        pop_deck = json.dumps(pop_deck, ensure_ascii=False)

        if len(deck_box)>1 and len(response.css('a.deck-box::attr(href)'))>1:
            best_deck_code = response.css('a.deck-box::attr(href)')[1].extract()
            best_deck_code = re.match('.*\/(.*)\/', best_deck_code).group(1)
            best_deck_win_rate = deck_box[1].css('div.stats-table tr')[0].css('td::text').extract_first('')
            best_deck_games = deck_box[1].css('div.stats-table tr')[1].css('td::text').extract_first('')
            best_deck = [best_deck_code, best_deck_win_rate, best_deck_games]
        else:
            best_deck = []
        best_deck = json.dumps(best_deck, ensure_ascii=False)

        matchup_box = response.css('a.matchup-box')
        if len(matchup_box)>0:
            best_matchup_player_class = matchup_box[0].css('span.player-class::text').extract_first('')
            if (best_matchup_player_class):
                best_matchup_win_rate = matchup_box[0].css('div.stats-table tr')[0].css('td::text').extract_first('')
                best_matchup_games = matchup_box[0].css('div.stats-table tr')[1].css('td::text').extract_first('')
                best_matchup = [best_matchup_player_class, best_matchup_win_rate, best_matchup_games]
            else:
                best_matchup = []
        else:
            print('yf_log: best_matchup matchup_box is null')
            best_matchup = []
        best_matchup = json.dumps(best_matchup, ensure_ascii=False)

        if len(matchup_box) > 1:
            worst_matchup_player_class = matchup_box[1].css('span.player-class::text').extract_first('')
            if worst_matchup_player_class:
                worst_matchup_win_rate = matchup_box[1].css('div.stats-table tr')[0].css('td::text').extract_first('')
                worst_matchup_games = matchup_box[1].css('div.stats-table tr')[1].css('td::text').extract_first('')
                worst_matchup = [worst_matchup_player_class, worst_matchup_win_rate, worst_matchup_games]
            else:
                worst_matchup = []
        else:
            print('yf_log: worst_matchup matchup_box is null')
            worst_matchup = []
        worst_matchup = json.dumps(worst_matchup, ensure_ascii=False)

        card_list_wrapper = response.css('div.archetype-signature div.card-list-wrapper')
        core_card_list_items = card_list_wrapper[0].css('div.card-tile') if len(card_list_wrapper)>0  else []
        core_cards = []
        for item in core_card_list_items:
            card_name = item.css('span.card-name::text').extract_first('')
            card_cost = item.css('span.card-cost::text').extract_first('')
            card_assert = item.css('img.card-asset::attr(src)').extract_first('')
            card_hsid = card_assert.split('/')[-1].split('.')[0]
            # core_cards.append([card_name, card_cost, card_assert])
            core_cards.append({'name': card_name, 'cost': card_cost, 'card_hsid': card_hsid})
        # core_cards = json.dumps(core_cards, ensure_ascii=False)

        pop_card_list_items = card_list_wrapper[1].css('div.card-tile') if len(card_list_wrapper)>1 else []
        pop_cards = []
        for item in pop_card_list_items:
            card_name = item.css('span.card-name::text').extract_first('')
            card_cost = item.css('span.card-cost::text').extract_first('')
            card_assert = item.css('img.card-asset::attr(src)').extract_first('')
            card_hsid = card_assert.split('/')[-1].split('.')[0]
            # pop_cards.append([card_name, card_cost, card_assert])
            pop_cards.append({'name': card_name, 'cost': card_cost, 'card_hsid': card_hsid})
        # pop_cards = json.dumps(pop_cards, ensure_ascii=False)

        hs_item = HSArchetypeSpiderItem()
        hs_item['tier'] = response.meta.get('tier')
        hs_item['faction'] = response.meta.get('faction')
        hs_item['archetype_name'] = response.meta.get('archetype_name')
        try:
            hs_item['win_rate'] = float(response.meta.get('win_rate').replace("%", ""))
        except Exception as e:
            print('yf_log', e, response.meta.get('win_rate'))
            hs_item['win_rate'] = 0
        try:
            hs_item['popularity'] = float(popularity)
        except Exception as e:
            print('yf_log', e, popularity)
            hs_item['popularity'] = 0
        hs_item['game_count'] = int(game_count)
        hs_item['best_matchup'] = best_matchup
        hs_item['worst_matchup'] = worst_matchup
        hs_item['pop_deck'] = pop_deck
        hs_item['best_deck'] = best_deck
        hs_item['core_cards'] = core_cards
        hs_item['pop_cards'] = pop_cards
        hs_item['matchup'] = "[]"

        self.crawler.stats.inc_value('archetypes_scraped')
        yield hs_item

    #     matchup_url = response.css('a#tab-matchups::attr(href)').extract_first('')
    #     url = parse.urljoin(response.url, matchup_url)
    #     yield Request(url=url, meta={
    #         'tier_meta': response.meta,
    #         'win_rate': win_rate,
    #         'game_count': game_count,
    #         'popularity': popularity,
    #         'best_matchup': best_matchup,
    #         'worst_matchup': worst_matchup,
    #         'pop_deck': pop_deck,
    #         'best_deck': best_deck,
    #         'core_cards': core_cards,
    #         'pop_cards': pop_cards,
    #     }, callback=self.matchup_detail, dont_filter=True)
    #
    # def matchup_detail(self, response):
    #     hs_item = HSArchetypeSpiderItem()
    #     hs_item['tier'] = response.meta.get('tier_meta').get('tier')
    #     hs_item['faction'] = response.meta.get('tier_meta').get('faction')
    #     hs_item['archetype_name'] = response.meta.get('tier_meta').get('archetype_name')
    #     hs_item['win_rate'] = float(response.meta.get('tier_meta').get('win_rate').replace("%", ""))
    #     # try:
    #     #     hs_item['win_rate'] = float(response.meta.get('win_rate'))
    #     # except Exception as e:
    #     #     print('yf_log', e, response.meta.get('win_rate'))
    #     #     hs_item['win_rate'] = 0
    #     try:
    #         hs_item['popularity'] = float(response.meta.get('popularity'))
    #     except Exception as e:
    #         print('yf_log', e, response.meta.get('popularity'))
    #         hs_item['popularity'] = 0
    #     hs_item['game_count'] = int(response.meta.get('game_count')) if response.meta.get('game_count') else None
    #     hs_item['best_matchup'] = response.meta.get('best_matchup')
    #     hs_item['worst_matchup'] = response.meta.get('worst_matchup')
    #     hs_item['pop_deck'] = response.meta.get('pop_deck')
    #     hs_item['best_deck'] = response.meta.get('best_deck')
    #     hs_item['core_cards'] = response.meta.get('core_cards')
    #     hs_item['pop_cards'] = response.meta.get('pop_cards')
    #
    #
    #     faction_boxes = response.css('div.class-box-container div.box.class-box')
    #     matchup = []
    #     for box in faction_boxes:
    #         faction = box.css('div.box-title span.player-class::text').extract_first('')
    #         archetype_list = box.css('div.grid-container')[2].css('a.player-class::text').extract()
    #         data_cells = box.css('div.grid-container')[3].css('a.table-cell::text').extract()
    #         data_list = []
    #         list = []
    #         for item in data_cells:
    #             list.append(item)
    #             if len(list) % 3 == 0:
    #                 data_list.append(list)
    #                 list = []
    #                 continue
    #         for i, archetype in enumerate(archetype_list):
    #             try:
    #                 data_list[i].insert(0, archetype)
    #             except Exception as e:
    #                 print(e, data_list, archetype_list)
    #         matchup.append(data_list)
    #     matchup = json.dumps(matchup, ensure_ascii=False)
    #     hs_item['matchup'] = matchup
    #     hs_item['date'] = datetime.datetime.now().strftime(SQL_FULL_DATETIME)
    #     self.crawler.stats.inc_value('archetypes_scraped')
    #     yield hs_item
