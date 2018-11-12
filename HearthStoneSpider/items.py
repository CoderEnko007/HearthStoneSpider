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
    mode = scrapy.Field() # 游戏模式
    faction  = scrapy.Field() # 职业
    deck_name = scrapy.Field() # 套牌名称
    dust_cost = scrapy.Field() # 合成花费
    win_rate = scrapy.Field() # 胜率
    real_win_rate = scrapy.Field()
    game_count = scrapy.Field() # 总对局数
    real_game_count = scrapy.Field() # 实际总对局数
    duration = scrapy.Field() # 对局时长
    background_img = scrapy.Field() # 背景图
    deck_code = scrapy.Field() #卡组代码

    card_list = scrapy.Field() # 卡组套牌
    turns = scrapy.Field() # 回合数
    faction_win_rate = scrapy.Field() # 各职业对战胜率
    date = scrapy.Field() # 日期

    trending_flag = scrapy.Field() # 是否为流行套牌
    last_30_days = scrapy.Field() # 是否为最近30天套牌

class HSArchetypeSpiderItem(scrapy.Item):
    tier = scrapy.Field() # 梯队
    faction = scrapy.Field() # 职业
    archetype_name = scrapy.Field() # 卡组模板名称
    win_rate = scrapy.Field() # 胜率
    game_count = scrapy.Field() # 对局数
    popularity = scrapy.Field() # 热度
    best_matchup = scrapy.Field() # 最优对局
    worst_matchup = scrapy.Field() # 最劣对局
    pop_deck = scrapy.Field() # 最受欢迎卡组
    best_deck = scrapy.Field() # 最优异卡组
    core_cards = scrapy.Field() # 核心卡牌
    pop_cards = scrapy.Field() # 热门卡牌
    matchup = scrapy.Field() # 各职业胜率
    date = scrapy.Field()  # 日期

class HSWinRateSpiderItem(scrapy.Item):
    faction = scrapy.Field() # 职业
    archetype  = scrapy.Field() # 套牌模型
    winrate  = scrapy.Field() # 胜率
    popularity  = scrapy.Field() # 热度
    games  = scrapy.Field() # 对局数

    faction_popularity = scrapy.Field()  # 热度
    real_winrate = scrapy.Field()
    real_games = scrapy.Field()
    best_matchup = scrapy.Field()  # 最优对局
    worst_matchup = scrapy.Field()  # 最劣对局
    pop_deck = scrapy.Field()  # 最受欢迎卡组
    best_deck = scrapy.Field()  # 最优异卡组
    core_cards = scrapy.Field()  # 核心卡牌
    pop_cards = scrapy.Field()  # 热门卡牌
    matchup = scrapy.Field()  # 各职业胜率
    date = scrapy.Field()  # 日期

class HSArenaCardsSpiderItem(scrapy.Item):
    dbfId = scrapy.Field()
    name = scrapy.Field()
    ename = scrapy.Field()
    hsId = scrapy.Field()
    cardClass = scrapy.Field()
    cost = scrapy.Field()
    attack = scrapy.Field()
    health = scrapy.Field()
    rarity = scrapy.Field()
    type = scrapy.Field()
    set_id = scrapy.Field()
    race = scrapy.Field()
    mechanics = scrapy.Field()
    flavor = scrapy.Field()
    text = scrapy.Field()
    artist = scrapy.Field()
    collectible = scrapy.Field()
    update_time = scrapy.Field()

    class_all = scrapy.Field()
    class_druid = scrapy.Field()
    class_hunter = scrapy.Field()
    class_mage = scrapy.Field()
    class_paladin = scrapy.Field()
    class_priest = scrapy.Field()
    class_rogue = scrapy.Field()
    class_shaman = scrapy.Field()
    class_warlock = scrapy.Field()
    class_warrior = scrapy.Field()
    # classification = scrapy.Field()
    # deck_pop = scrapy.Field()
    # copies = scrapy.Field()
    # deck_winrate = scrapy.Field()
    #
    # times_played = scrapy.Field()
    # played_pop = scrapy.Field()
    # played_winrate = scrapy.Field()
