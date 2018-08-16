# -*- coding: utf-8 -*-
import scrapy
import math
from json import loads

from HearthStoneSpider.items import HearthstonespiderItem, HearthstonesItemLoader
from scrapy.loader import ItemLoader

class HearthstoneSpider(scrapy.Spider):
    name = 'HearthStone'
    allowed_domains = ['www.iyingdi.com']
    base_url = 'https://www.iyingdi.com/hearthstone/card/search/vertical'
    def start_requests(self):
        formdata = {'statistic': 'total'}
        return [scrapy.FormRequest(self.base_url, formdata=formdata, callback=self.parse)]

    def parse(self, response):
        res_json = loads(response.text)
        page_size = 30
        page_nums = int(math.ceil(res_json.get('data').get('total')/page_size))
        for page in range(page_nums):
            formdata = {
                'statistic': 'total',
                'order': '-series,+mana',
                'size': str(page_size),
                'page': str(page)
            }
            yield scrapy.FormRequest(self.base_url, formdata=formdata, callback=self.parse_detail)

    def parse_detail(self, response):
        res_json = loads(response.text)
        cards = res_json.get('data').get('cards')

        for card in cards:
            hs_item = HearthstonespiderItem()
            hs_item['mana'] = card.get('mana')
            hs_item['hp'] = card.get('hp')
            hs_item['attack'] = card.get('attack')
            hs_item['cname'] = card.get('cname')
            hs_item['description'] = card.get('description')
            hs_item['ename'] = card.get('ename')
            hs_item['faction'] = card.get('faction')
            hs_item['clazz'] = card.get('clazz')
            hs_item['race'] = card.get('race')
            hs_item['rarity'] = card.get('rarity')
            hs_item['rule'] = card.get('rule')
            hs_item['seriesAbbr'] = card.get('seriesAbbr')
            hs_item['seriesName'] = card.get('seriesName')
            hs_item['standard'] = card.get('standard')
            hs_item['wild'] = card.get('wild')
            hs_item['img'] = [card.get('img')]
            hs_item['thumbnail'] = [card.get('thumbnail')]

            # item_loader = HearthstonesItemLoader(item=HearthstonespiderItem(), response=response)
            # item_loader.add_value('mana', card.get('mana'))
            # item_loader.add_value('hp', card.get('hp'))
            # item_loader.add_value('attack', card.get('attack'))
            # item_loader.add_value('cname', card.get('cname'))
            # item_loader.add_value('description', card.get('description'))
            # item_loader.add_value('ename', card.get('ename'))
            # item_loader.add_value('faction', card.get('faction'))
            # item_loader.add_value('clazz', card.get('clazz'))
            # item_loader.add_value('race', card.get('race'))
            # item_loader.add_value('rarity', card.get('rarity'))
            # item_loader.add_value('rule', card.get('rule'))
            # item_loader.add_value('seriesAbbr', card.get('seriesAbbr'))
            # item_loader.add_value('seriesName', card.get('seriesName'))
            # item_loader.add_value('standard', card.get('standard'))
            # item_loader.add_value('wild', card.get('wild'))
            # item_loader.add_value('img', card.get('img'))
            # item_loader.add_value('thumbnail', card.get('thumbnail'))
            #
            # hs_item = item_loader.load_item()
            yield hs_item