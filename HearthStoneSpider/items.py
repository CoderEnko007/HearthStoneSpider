# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

class HearthstonesItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()

class HearthstonespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    mana = scrapy.Field() # 费用
    hp = scrapy.Field() # 血量
    attack = scrapy.Field() # 攻击
    cname = scrapy.Field() # 名称
    description = scrapy.Field() #描述
    ename = scrapy.Field() #英文名
    faction = scrapy.Field() #职业
    clazz = scrapy.Field() # 卡牌类别
    race = scrapy.Field() # 种族
    rarity = scrapy.Field() # 稀有度
    rule = scrapy.Field() # 卡牌效果说明
    seriesAbbr = scrapy.Field() # 系列简称
    seriesName = scrapy.Field() # 系列中文全名称
    standard = scrapy.Field() # 标准模式
    wild = scrapy.Field() # 狂野模式

    img = scrapy.Field() # 图片
    # img_path = scrapy.Field() # 本地存储地址
    thumbnail = scrapy.Field() #缩略图

class HSReportSpiderItem(scrapy.Item):
    rank_no = scrapy.Field() # 排名
    name = scrapy.Field() # 职业
    winrate = scrapy.Field() # 胜率
    mode = scrapy.Field() # 模式
    date = scrapy.Field() # 日期

class HSDecksSpiderItem(scrapy.Item):
    deck_id = scrapy.Field() # 卡组id
    faction  = scrapy.Field() # 职业
    deck_name = scrapy.Field() # 套牌名称
    dust_cost = scrapy.Field() # 合成花费
    win_rate = scrapy.Field() # 胜率
    game_count = scrapy.Field() # 总对局数
    duration = scrapy.Field() # 对局时长
    background_img = scrapy.Field() # 背景图