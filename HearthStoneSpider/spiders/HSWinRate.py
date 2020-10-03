# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
import requests
import copy
import time
import platform
from urllib import parse
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals
from scrapy.http import Request
from scrapy.http import HtmlResponse

from HearthStoneSpider.items import HSWinRateSpiderItem
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME, CHANGE_LANGUAGE


class HSWinRateSpider(scrapy.Spider):
    name = 'HSWinRate'
    allowed_domains = ['hsreplay.net/meta/#tab=archetypes']
    start_urls = ['https://hsreplay.net/meta/#tab=archetypes']
    # start_urls = ['https://hsreplay.net/meta/#tab=archetypes&timeFrame=LAST_7_DAYS']

    def __init__(self, rankRangeParams=None, timeFrame=None, faction=None, archetype=None):
        super(HSWinRateSpider, self).__init__()
        if rankRangeParams == 'ALL':
            self.start_urls = [
                'https://hsreplay.net/meta/#tab=archetypes{}'.format('&timeFrame=' + timeFrame if timeFrame else ''),
                'https://hsreplay.net/meta/#tab=archetypes&rankRange=DIAMOND_THROUGH_LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else ''),
                'https://hsreplay.net/meta/#tab=archetypes&rankRange=DIAMOND_FOUR_THROUGH_DIAMOND_ONE{}'.format('&timeFrame=' + timeFrame if timeFrame else ''),
                'https://hsreplay.net/meta/#tab=archetypes&rankRange=LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else ''),
                'https://hsreplay.net/meta/#tab=archetypes&rankRange=TOP_1000_LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else '')]
        elif rankRangeParams == 'DIAMOND_THROUGH_LEGEND':
            self.start_urls = ['https://hsreplay.net/meta/#tab=archetypes&rankRange=DIAMOND_THROUGH_LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else '')]
        elif rankRangeParams == 'LEGEND':
            self.start_urls = ['https://hsreplay.net/meta/#tab=archetypes&rankRange=LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else '')]
        elif rankRangeParams == 'DIAMOND_FOUR_THROUGH_DIAMOND_ONE':
            self.start_urls = ['https://hsreplay.net/meta/#tab=archetypes&rankRange=DIAMOND_FOUR_THROUGH_DIAMOND_ONE{}'.format('&timeFrame=' + timeFrame if timeFrame else '')]
        elif rankRangeParams == 'TOP_1000_LEGEND':
            self.start_urls = ['https://hsreplay.net/meta/#tab=archetypes&rankRange=TOP_1000_LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else '')]
        elif rankRangeParams == 'VIP':
            self.start_urls = [
                'https://hsreplay.net/meta/#tab=archetypes&rankRange=DIAMOND_THROUGH_LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else ''),
                'https://hsreplay.net/meta/#tab=archetypes&rankRange=DIAMOND_FOUR_THROUGH_DIAMOND_ONE{}'.format('&timeFrame=' + timeFrame if timeFrame else ''),
                'https://hsreplay.net/meta/#tab=archetypes&rankRange=LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else ''),
                'https://hsreplay.net/meta/#tab=archetypes&rankRange=TOP_1000_LEGEND{}'.format('&timeFrame=' + timeFrame if timeFrame else '')]
        else:
            self.start_urls = ['https://hsreplay.net/meta/#tab=archetypes{}'.format('&timeFrame=' + timeFrame if timeFrame else '')]
        self.rankRangeParams = rankRangeParams if rankRangeParams else 'BRONZE_THROUGH_GOLD'
        self.faction = eval(faction)if faction else None
        self.archetype = archetype
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('--disable-gpu')
        chrome_opt.add_argument('--no-sandbox')
        if platform.platform().find('Linux') != -1:
            chrome_opt.add_argument('blink-settings=imagesEnabled=false') # 无图模式
            chrome_opt.add_argument('--headless')  # 无页面模式
        else:
            chrome_opt.add_argument('blink-settings=imagesEnabled=false')
        self.browser = webdriver.Chrome(chrome_options=chrome_opt)
        dispatcher.connect(self.spider_closed, signals.spider_closed)  # scrapy信号量，spider退出时关闭browser
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)
        self.addCookieFlag = True
        # if platform.platform().find('Windows') != -1:
        #     self.addCookieFlag = True
        # else:
        #     self.addCookieFlag = False if self.rankRangeParams == 'BRONZE_THROUGH_GOLD' else True
        # self.langToggleClicked = False

    def spider_closed(self):
        time.sleep(5)
        print('HSWinRate end')
        self.browser.quit()

    def engine_stopped(self):
        print('HSReport engine end')
        # requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/8gI1Ku43Py') # HSWinRateWebHook
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/elzp6Ttp2L') # HSWinrateRangeDataWebHook
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/ey491UwqmO') # HSWinRateArchetypeWebHook


    def parse(self, response):
        if self.rankRangeParams == 'VIP' or self.rankRangeParams == 'ALL':
            reg_range = re.findall('.*rankRange=([0-9, a-z, A-Z, _]*)', response.url)
            rankRange = reg_range[0] if len(reg_range) else 'BRONZE_THROUGH_GOLD'
        elif self.rankRangeParams:
            rankRange = self.rankRangeParams
        else:
            rankRange = 'BRONZE_THROUGH_GOLD'
        if CHANGE_LANGUAGE and not self.langToggleClicked and platform.platform().find('Windows') != -1:
            langToggle = self.browser.find_elements_by_css_selector('.dropdown-toggle')[0]
            langToggle.click()
            time.sleep(3)
            langItemEn = self.browser.find_elements_by_css_selector('.dropdown-menu li')[0]
            langItemEn.click()
            time.sleep(3)
            classBtn = self.browser.find_elements_by_css_selector('#tab-archetypes')[0]
            classBtn.click()
            time.sleep(3)
            self.langToggleClicked = True
            response = HtmlResponse(
                url=self.browser.current_url,
                body=self.browser.page_source,
                encoding='utf-8',
            )
        faction_boxes = response.css('div.class-box-container div.box.class-box')
        for box in faction_boxes:
            faction = box.css('div.box-title span.player-class::text').extract_first('')
            faction = faction.replace(' ', '')
            self.faction = [faction.lower() for faction in self.faction] if self.faction else None
            if self.faction and faction.lower() not in self.faction:
                continue
            archetype_list = box.css('div.grid-container')[2].css('a.player-class::text').extract()
            archetype_list_other_item = box.css('div.grid-container')[2].css('span.player-class div.tooltip-wrapper::text').extract_first('')
            if archetype_list_other_item:
                archetype_list.append(archetype_list_other_item)
            detail_url_list = box.css('div.grid-container')[2].css('a.player-class::attr(href)').extract()
            detail_url_list.append('')
            data_cells = box.css('div.grid-container')[3].css('.table-cell::text').extract()
            data_list = []
            list_temp = []
            for item in data_cells:
                list_temp.append(item)
                if len(list_temp)%3 == 0:
                    data_list.append(list_temp)
                    list_temp = []
                    continue
            for i, archetype in enumerate(archetype_list):
                if self.archetype and archetype.lower() != self.archetype.lower():
                    continue
                hs_item = HSWinRateSpiderItem()
                hs_item['rank_range'] = '_'.join([x.upper() for x in rankRange.split('_')])
                hs_item['faction'] = faction.capitalize()
                if hs_item['faction'] == 'Demonhunter':
                    hs_item['faction'] = 'DemonHunter'
                hs_item['archetype'] = archetype
                win_rate = re.findall('\d+', data_list[i][0])
                hs_item['winrate'] = float('.'.join(win_rate))
                popularity = re.findall('\d+', data_list[i][1])
                hs_item['popularity'] = float('.'.join(popularity))
                hs_item['games'] = int(data_list[i][2].replace(',', ''))
                hs_item['date'] = datetime.datetime.now().strftime(SQL_FULL_DATETIME)
                detail_url = parse.urljoin('https://hsreplay.net', detail_url_list[i])
                if detail_url_list[i] != '' and rankRange=='BRONZE_THROUGH_GOLD':
                    print('detail_url:', detail_url)
                    rank_range_url = "{}#rankRange=DIAMOND_THROUGH_LEGEND".format(detail_url)
                    yield Request(url=rank_range_url, meta=hs_item, callback=self.parse_detail, dont_filter=True)
                else:
                    yield hs_item

    def parse_detail(self, response):
        hs_item = copy.copy(response.meta)
        win_rate = response.css('a.winrate-box .box-content h1::text').extract_first('')
        win_rate = re.findall('\d+', win_rate)
        win_rate = '.'.join(win_rate)
        if win_rate:
            hs_item['real_winrate'] = float(win_rate)
        else:
            hs_item['real_winrate'] = hs_item['winrate']
        game_count = response.css('a.winrate-box .box-content h3::text').extract_first('')
        game_count = re.findall('\d+', game_count)
        game_count = ''.join(game_count)
        if game_count:
            hs_item['real_games'] = int(game_count)
        else:
            hs_item['real_games'] = hs_item['games']
        popularity = response.css('a.popularity-box .box-content h1::text').extract_first('')
        popularity = re.findall('\d+', popularity)
        popularity = '.'.join(popularity)
        if popularity:
            hs_item['faction_popularity'] = float(popularity)
        else:
            hs_item['faction_popularity'] = 0

        deck_box = response.css('a.deck-box')
        if len(deck_box) > 0:
            pop_deck_code = response.css('a.deck-box::attr(href)').extract()
            if pop_deck_code:
                pop_deck_code = pop_deck_code[0]
                pop_deck_code = re.match('.*\/(.*)\/', pop_deck_code).group(1)
                pop_deck_win_rate = deck_box[0].css('div.stats-table tr')[0].css('td::text').extract_first('')
                pop_deck_games = deck_box[0].css('div.stats-table tr')[1].css('td::text').extract_first('')
                pop_deck = [pop_deck_code, pop_deck_win_rate, pop_deck_games]
            else:
                print('{} pop_deck is none'.format(hs_item['archetype']))
                pop_deck = []
        else:
            pop_deck = []
        pop_deck = json.dumps(pop_deck, ensure_ascii=False)
        hs_item['pop_deck'] = pop_deck

        if len(deck_box) > 1:
            best_deck_code = response.css('a.deck-box::attr(href)').extract()
            if best_deck_code:
                best_deck_code = best_deck_code[1]
                best_deck_code = re.match('.*\/(.*)\/', best_deck_code).group(1)
                best_deck_win_rate = deck_box[1].css('div.stats-table tr')[0].css('td::text').extract_first('')
                best_deck_games = deck_box[1].css('div.stats-table tr')[1].css('td::text').extract_first('')
                best_deck = [best_deck_code, best_deck_win_rate, best_deck_games]
            else:
                print('{} best_deck is none'.format(hs_item['archetype']))
                best_deck = []
        else:
            best_deck = []
        best_deck = json.dumps(best_deck, ensure_ascii=False)
        hs_item['best_deck'] = best_deck

        matchup_box = response.css('a.matchup-box')
        if len(matchup_box) > 0:
            best_matchup_player_class = matchup_box[0].css('span.player-class::text').extract_first('')
            best_matchup_faction = matchup_box[0].css('span.player-class::attr(class)').extract_first('')
            best_matchup_faction = best_matchup_faction.split(' ')[-1].capitalize()
            if best_matchup_faction == 'Demonhunter':
                best_matchup_faction = 'DemonHunter'
            matchup_box_tr = matchup_box[0].css('div.stats-table tr')
            if len(matchup_box_tr) > 1:
                best_matchup_win_rate = matchup_box_tr[0].css('td::text').extract_first('')
                best_matchup_games = matchup_box_tr[1].css('td::text').extract_first('')
                best_matchup = [best_matchup_player_class, best_matchup_win_rate, best_matchup_games, best_matchup_faction]
            else:
                print('{} best_matchup matchup_box_tr is null'.format(hs_item['archetype']))
                best_matchup = []
        else:
            print('{} best_matchup matchup_box is null'.format(hs_item['archetype']))
            best_matchup = []
        best_matchup = json.dumps(best_matchup, ensure_ascii=False)
        hs_item['best_matchup'] = best_matchup

        if len(matchup_box) > 1:
            worst_matchup_player_class = matchup_box[1].css('span.player-class::text').extract_first('')
            worst_matchup_faction_t = matchup_box[1].css('span.player-class::attr(class)').extract_first('')
            worst_matchup_faction = worst_matchup_faction_t.split(' ')[-1].capitalize()
            if worst_matchup_faction == 'Demonhunter':
                worst_matchup_faction = 'DemonHunter'
            matchup_box_tr = matchup_box[1].css('div.stats-table tr')
            if len(matchup_box_tr) > 1:
                worst_matchup_win_rate = matchup_box[1].css('div.stats-table tr')[0].css('td::text').extract_first('')
                worst_matchup_games = matchup_box[1].css('div.stats-table tr')[1].css('td::text').extract_first('')
                worst_matchup = [worst_matchup_player_class, worst_matchup_win_rate, worst_matchup_games, worst_matchup_faction]
            else:
                print('yf_log: worst_matchup matchup_box_tr is null ')
                worst_matchup = []
        else:
            print('yf_log: worst_matchup matchup_box is null')
            worst_matchup = []
        worst_matchup = json.dumps(worst_matchup, ensure_ascii=False)
        hs_item['worst_matchup'] = worst_matchup

        card_list_wrapper = response.css('div.archetype-signature div.card-list-wrapper')
        core_card_list_items = card_list_wrapper[0].css('.card-tile') if len(card_list_wrapper) > 0 else []
        core_cards = []
        for item in core_card_list_items:
            card_name = item.css('.card-name::text').extract_first('')
            card_cost = item.css('.card-cost::text').extract_first('')
            card_assert = item.css('img.card-asset::attr(src)').extract_first('')
            card_hsid = card_assert.split('/')[-1].split('.')[0]
            # core_cards.append([card_name, card_cost, card_assert])
            core_cards.append({'name': card_name, 'cost': card_cost, 'card_hsid': card_hsid})
        hs_item['core_cards'] = core_cards

        pop_card_list_items = card_list_wrapper[1].css('.card-tile') if len(card_list_wrapper) > 1 else []
        pop_cards = []
        for item in pop_card_list_items:
            card_name = item.css('.card-name::text').extract_first('')
            card_cost = item.css('.card-cost::text').extract_first('')
            card_assert = item.css('img.card-asset::attr(src)').extract_first('')
            card_hsid = card_assert.split('/')[-1].split('.')[0]
            # pop_cards.append([card_name, card_cost, card_assert])
            pop_cards.append({'name': card_name, 'cost': card_cost, 'card_hsid': card_hsid})
        hs_item['pop_cards'] = pop_cards

        # matchup_url = response.css('a#tab-matchups::attr(href)').extract_first('')
        url = "{}&tab=matchups".format(response.url)
        # url = parse.urljoin(response.url, matchup_url)
        yield Request(url=url, meta=hs_item, callback=self.matchup_detail, dont_filter=True)

    def matchup_detail(self, response):
        hs_item = copy.copy(response.meta)
        faction_boxes = response.css('div.class-box-container div.box.class-box')
        matchup = {'Druid':[], 'Hunter':[], 'Mage':[], 'Paladin':[], 'Priest':[], 'Rogue':[], 'Shaman':[], 'Warlock':[], 'Warrior':[], 'DemonHunter':[]}
        for box in faction_boxes:
            faction = box.css('div.box-title span.player-class::text').extract_first('').replace(' ', '')
            archetype_list = box.css('div.grid-container')[2].css('a.player-class::text').extract()
            data_cells = box.css('div.grid-container')[3].css('a.table-cell::text').extract()
            data_list = []
            list_temp = []
            for item in data_cells:
                list_temp.append(item)
                if len(list_temp) % 3 == 0:
                    data_list.append(list_temp)
                    list_temp = []
                    continue
            for i, archetype in enumerate(archetype_list):
                try:
                    data_list[i].insert(0, archetype)
                except Exception as e:
                    print(e, data_list, archetype_list)
            # matchup.append(data_list)
            matchup[faction] = data_list
        matchup = json.dumps(list(matchup.values()), ensure_ascii=False)
        hs_item['matchup'] = matchup
        yield hs_item

    # matchup_tab = self.browser.find_elements_by_css_selector('#tab-matchups')[0]
    # while matchup_tab.is_displayed():
    #     time.sleep(1)
    # matchup_tab.click()
    # time.sleep(1)
    # t_selector = Selector(text=self.browser.page_source)
    # faction_boxes = t_selector.css('div.class-box-container div.box.class-box')
    # matchup = {'Druid': [], 'Hunter': [], 'Mage': [], 'Paladin': [], 'Priest': [], 'Rogue': [], 'Shaman': [],
    #            'Warlock': [], 'Warrior': []}
    # for box in faction_boxes:
    #     faction = box.css('div.box-title span.player-class::text').extract_first('')
    #     archetype_list = box.css('div.grid-container')[2].css('a.player-class::text').extract()
    #     data_cells = box.css('div.grid-container')[3].css('a.table-cell::text').extract()
    #     data_list = []
    #     list_temp = []
    #     for item in data_cells:
    #         list_temp.append(item)
    #         if len(list_temp) % 3 == 0:
    #             data_list.append(list_temp)
    #             list_temp = []
    #             continue
    #     for i, archetype in enumerate(archetype_list):
    #         try:
    #             data_list[i].insert(0, archetype)
    #         except Exception as e:
    #             print(e, data_list, archetype_list)
    #     # matchup.append(data_list)
    #     matchup[faction] = data_list
    # matchup = json.dumps(list(matchup.values()), ensure_ascii=False)
    # hs_item['matchup'] = matchup
    # yield hs_item

