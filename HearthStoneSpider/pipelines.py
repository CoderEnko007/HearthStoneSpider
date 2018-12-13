# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don"t forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import json
import copy
from datetime import datetime

from twisted.enterprise import adbapi
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum
from scrapy.exporters import JsonItemExporter

import MySQLdb
import MySQLdb.cursors

from HearthStoneSpider.tools.pyhearthstone import HearthStoneDeck
from HearthStoneSpider.settings import SQL_FULL_DATETIME

class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.RARITY_TYPE = {'1': '基本', '2': '普通', '3': '稀有', '4': '史诗', '5': '传说'}
        self.SERIES_TYPE = {'1': 'BASIC', '2': 'NAXX', '3': 'GVG', '4': 'BRM', '5': 'TGT', '6': 'LOE', '7': 'WOG',
                            '8': 'ONK', '9': 'MSG', '10': 'JUG', '11': 'KFT', '12': 'KNC', '13': 'TWW', '14': 'tableP'}
        self.CLAZZ_TYPE = {'1': '随从', '2': '法术', '3': '装备', '4': '英雄牌'}
        self.MODE_TYPE = {'Standard': '标准模式', 'Wild': '狂野模式'}

    def get_key(self, dict, value):
        if value=='':
            return ['']
        return [k for k, v in dict.items() if v == value]

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PWD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)  # 可变化参数传值
        return cls(dbpool)

    def insert(self, cursor, data, table):
        ls = [(k, data[k]) for k in data if data[k]]
        sql = 'insert into %s (' % table + ','.join([i[0] for i in ls]) + \
              ') values (' + ','.join(['%r' % i[1] for i in ls]) + ');'
        cursor.execute(sql)
        print('insert', data['name'], data['classification'])

    def update(self, cursor, dt_update, dt_condition, table):
        sql = 'UPDATE %s SET ' % table + ','.join(['%s=%r' % (k, dt_update[k]) for k in dt_update]) \
              + ' WHERE ' + ' AND '.join(['%s=%r' % (k, dt_condition[k]) for k in dt_condition]) + ';'
        cursor.execute(sql)
        print('update', dt_update['name'], dt_update['classification'])

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        asynItem = copy.deepcopy(item) # 在通过api爬取数据时，由于速度很快，item会被后面的数据覆盖，因此这里改为深拷贝
        global query
        asyncItem = copy.deepcopy(item)
        if spider.name=='HearthStone':
            query = self.dbpool.runInteraction(self.update_cards, asyncItem)
        elif spider.name=='HSReport':
            query = self.dbpool.runInteraction(self.update_rank, asynItem)
        elif spider.name=='HSDecks' or spider.name=='HSWildDecks':
            query = self.dbpool.runInteraction(self.update_decks, asynItem, spider)
        elif spider.name=='HSWinRate':
            query = self.dbpool.runInteraction(self.update_winrate, asynItem)
        elif spider.name=='HSArchetype':
            query = self.dbpool.runInteraction(self.update_archetype, asynItem)
        elif spider.name=='HSArenaCards':
            query = self.dbpool.runInteraction(self.update_arena_cards, asynItem, spider)
        if query is not None:
            query.addErrback(self.handle_err, asynItem)

    def handle_err(self, failure, item):
        # 处理异步插入的异常
        print('错误:', failure)
        # print('aaaaaaa', item)

    def update_archetype(self, cursor, item):
        core_cards = item['core_cards']
        pop_cards = item['pop_cards']
        for cards in [core_cards, pop_cards]:
            for card in cards:
                select_sql = "SELECT * FROM cards_hscards WHERE ename=%r" % card['name']
                cursor.execute(select_sql)
                res_card = cursor.fetchone()
                card.update({'dbfId': res_card.get('dbfId')})
                card.update({'rarity': res_card.get('rarity')})
                card.update({'cname': res_card.get('name')})
        item['core_cards'] = json.dumps(item['core_cards'], ensure_ascii=False)
        item['pop_cards'] = json.dumps(item['pop_cards'], ensure_ascii=False)
        select_sql = "SELECT * FROM archetype_archetype WHERE archetype_name=%r AND to_days(update_time)=to_days(now())" % item['archetype_name']
        res = cursor.execute(select_sql)
        # print('测试：', item['archetype_name'], res)
        if res>0:
            update_sql = "update archetype_archetype set tier=%r, faction=%r, win_rate=%f, game_count=%d, popularity=%f, best_matchup=%r, worst_matchup=%r," \
                         " pop_deck=%r, best_deck=%r, core_cards=%r, pop_cards=%r, matchup=%r, update_time=%r where archetype_name=%r AND to_days(update_time)=to_days(now())"\
                         % (item['tier'], item['faction'], item['win_rate'], item['game_count'], item['popularity'], item['best_matchup'], item['worst_matchup'],\
                         item['pop_deck'], item['best_deck'], item['core_cards'], item['pop_cards'], item['matchup'], item['date'], item['archetype_name'])
            cursor.execute(update_sql)
        else:
            insert_sql = """
                insert into archetype_archetype(tier, faction, archetype_name, win_rate, game_count, popularity, best_matchup, worst_matchup, pop_deck, best_deck, core_cards, pop_cards, matchup, update_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (item['tier'], item['faction'], item['archetype_name'], item['win_rate'], item['game_count'], item['popularity'],
                                        item['best_matchup'], item['worst_matchup'], item['pop_deck'], item['best_deck'], item['core_cards'], item['pop_cards'], item['matchup'], item['date']))
        print('update archetype', item['archetype_name'])

    def update_winrate(self, cursor, item):
        if item['archetype'] != 'Other':
            core_cards = item.get('core_cards')
            pop_cards = item.get('pop_cards')
            for cards in [core_cards, pop_cards]:
                for card in cards:
                    select_sql = "SELECT * FROM cards_hscards WHERE ename=%r" % card['name']
                    cursor.execute(select_sql)
                    res_card = cursor.fetchone()
                    card.update({'dbfId': res_card.get('dbfId')})
                    card.update({'rarity': res_card.get('rarity')})
                    card.update({'cname': res_card.get('name')})
            item['core_cards'] = json.dumps(item.get('core_cards'), ensure_ascii=False)
            item['pop_cards'] = json.dumps(item.get('pop_cards'), ensure_ascii=False)
        select_sql = "SELECT * FROM winrate_hswinrate WHERE faction=%r AND archetype=%r AND to_days(create_time)=to_days(now())"\
                     % (item['faction'], item['archetype'])
        res = cursor.execute(select_sql)
        if res > 0:
            if item['archetype'] != 'Other':
                update_sql = "update winrate_hswinrate set winrate=%f, popularity=%f, games=%d, faction_popularity=%f, real_winrate=%f, real_games=%d, best_matchup=%r, worst_matchup=%r," \
                             "pop_deck=%r, best_deck=%r, core_cards=%r, pop_cards=%r, matchup=%r, create_time=%r " \
                             "where faction=%r AND archetype=%r AND to_days(create_time)=to_days(now())" \
                             % (item['winrate'], item['popularity'], item['games'], item['faction_popularity'], item['real_winrate'], item['real_games'], item['best_matchup'], item['worst_matchup'],
                                item['pop_deck'], item['best_deck'], item['core_cards'], item['pop_cards'], item['matchup'], item['date'], item['faction'], item['archetype'])
            else:
                update_sql = "update winrate_hswinrate set winrate=%f, popularity=%f, games=%d, create_time=%r where faction=%r AND archetype=%r AND to_days(create_time)=to_days(now())" \
                             % (item['winrate'], item['popularity'], item['games'], item['date'], item['faction'], item['archetype'])

            cursor.execute(update_sql)
        else:
            if item['archetype'] != 'Other':
                insert_sql = """
                    insert into winrate_hswinrate(faction, archetype, winrate, popularity, games, faction_popularity, real_winrate, real_games, best_matchup, worst_matchup, pop_deck, best_deck, core_cards, pop_cards, matchup, create_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (item['faction'], item['archetype'], item['winrate'], item['popularity'], item['games'], item['faction_popularity'], item['real_winrate'], item['real_games'],
                                            item['best_matchup'], item['worst_matchup'], item['pop_deck'], item['best_deck'], item['core_cards'], item['pop_cards'], item['matchup'], item['date']))
            else:
                insert_sql = """
                    insert into winrate_hswinrate(faction, archetype, winrate, popularity, games, create_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (item['faction'], item['archetype'], item['winrate'], item['popularity'], item['games'], item['date']))

    def update_decks(self, cursor, item, spider):
        hsCards = []
        deck_code = []
        clazzCount = {'MINION': 0, 'SPELL': 0, 'WEAPON': 0, 'HERO': 0} # 类别组成
        rarityCount = {'FREE': 0, 'COMMON': 0, 'RARE': 0, 'EPIC': 0, 'LEGENDARY': 0} # 稀有统计
        statistic = [0]*8 # 费用统计
        card_list = item['card_list']
        try:
            for card in card_list:
                select_sql = "SELECT * FROM cards_hscards WHERE ename=%r" % card['name']
                cursor.execute(select_sql)
                res_card = cursor.fetchone()
                # 用于生成卡组代码
                count = card.get('count')
                hsCards.append((res_card.get('dbfId'), count))
                # 套牌组成数据统计
                clazzCount[res_card.get('type')] += count
                rarityCount[res_card.get('rarity')] += count
                if (res_card.get('cost') >= 7):
                    statistic[7] += count
                else:
                    statistic[res_card.get('cost')] += count
                card.update({'dbfId': res_card.get('dbfId')})
                card.update({'rarity': res_card.get('rarity')})
                card.update({'cname': res_card.get('name')})
            hsDeck = HearthStoneDeck(hero=item['faction'], cards=hsCards)
            deck_code = hsDeck.genDeckString()
        except Exception as e:
            print('generate deck code error', e)
        item['card_list'] = json.dumps(item['card_list'], ensure_ascii=False)
        clazzCount = json.dumps(clazzCount, ensure_ascii=False)
        rarityCount = json.dumps(rarityCount, ensure_ascii=False)
        statistic = json.dumps(statistic, ensure_ascii=False)

        if item['trending_flag']:
            sql_name = 'decks_trending'
            tableID = spider.ifanr.tablesID['trending']
            query = {
                'where': json.dumps({
                    'faction': {'$eq': item['faction']}
                })
            }
            res = spider.ifanr.get_table_data(tableID=tableID, query=query)
        else:
            sql_name = 'decks_decks'
            # tableID = spider.ifanr.tablesID['decks_decks']
            if item['mode'] == 'Wild':
                tableID = spider.ifanr.tablesID['wild_decks']
            else:
                tableID = spider.ifanr.tablesID['standard_decks']
            # 知晓云数据库处理
            query = {
                'where': json.dumps({
                    'deck_id': {'$eq': item['deck_id']}
                }),
            }
            res = spider.ifanr.get_table_data(tableID=tableID, query=query)
        data = dict(item._values, **{
            'deck_code': deck_code,
            'clazzCount': clazzCount,
            'rarityCount': rarityCount,
            'statistic': statistic,
            'create_time': datetime.now().strftime(SQL_FULL_DATETIME)
        })
        if not item['trending_flag']:
            data['dust_cost'] = int(data['dust_cost'])
        if res:
            if (res.get('meta').get('total_count')):
                deck = res.get('objects')[0] if res.get('objects') else 'not found deck_id:%s' % deck_id
                if item['last_30_days'] and not item['trending_flag']:
                    data.pop('last_30_days')
                    data.pop('win_rate')
                    data.pop('game_count')
                print('last_30_days:', item['last_30_days'])
                spider.ifanr.put_table_data(tableID=tableID, id=deck['id'], data=data)
            else:
                spider.ifanr.add_table_data(tableID=tableID, data=data)
        else:
            print('yf_log res is none')

        # 阿里云数据库操作
        if item['trending_flag']:
            select_sql = "SELECT * FROM %s WHERE deck_id=%r" % (sql_name, item['deck_id'])
            res = cursor.execute(select_sql)
            if res>0:
                # 最近30天的卡组包含最新补丁卡组，所以最近30天卡组不更新last_30_days字段，防止最新补丁的卡组被覆盖为老卡组
                if item['last_30_days']:
                    update_sql = "update %s set faction=%r, deck_name=%r, dust_cost=%r, win_rate=%r, game_count=%r, real_game_count=%r, duration=%r, background_img=%r," \
                                 " card_list=%r, deck_code=%r, clazzCount=%r, rarityCount=%r, statistic=%r, turns=%r, faction_win_rate=%r, create_time=%r where deck_id=%r" \
                                 % (sql_name, item['faction'], item['deck_name'], item['dust_cost'], item['win_rate'], item['game_count'], item['real_game_count'], item['duration'], item['background_img'],
                                    item['card_list'], deck_code, clazzCount, rarityCount, statistic, item['turns'], item['faction_win_rate'], item['date'], item['deck_id'])
                else:
                    update_sql = "update %s set faction=%r, deck_name=%r, dust_cost=%r, win_rate=%r, game_count=%r, real_game_count=%r, duration=%r, background_img=%r," \
                                 " last_30_days=%s, card_list=%r, deck_code=%r, clazzCount=%r, rarityCount=%r, statistic=%r, turns=%r, faction_win_rate=%r, create_time=%r where deck_id=%r" \
                                 % (sql_name, item['faction'], item['deck_name'], item['dust_cost'], item['win_rate'], item['game_count'], item['real_game_count'], item['duration'], item['background_img'],
                                    item['last_30_days'], item['card_list'], deck_code, clazzCount, rarityCount, statistic, item['turns'], item['faction_win_rate'], item['date'], item['deck_id'])
                cursor.execute(update_sql)
                print('update deck', item['deck_id'], item['mode'])
            else:
                if sql_name == 'decks_trending':
                    insert_sql = """
                        insert into decks_trending(deck_id, faction, deck_name, dust_cost, win_rate, game_count, real_game_count, duration, background_img, card_list, deck_code, clazzCount, rarityCount, statistic, turns, faction_win_rate, create_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql,(item['deck_id'], item['faction'], item['deck_name'], item['dust_cost'], item['win_rate'], item['game_count'], item['real_game_count'], item['duration'],
                                               item['background_img'], item['card_list'], deck_code, clazzCount, rarityCount, statistic, item['turns'], item['faction_win_rate'], item['date']))
                else:
                    insert_sql = """
                        insert into decks_decks(mode, deck_id, faction, deck_name, dust_cost, win_rate, game_count, real_game_count, duration, background_img,
                         last_30_days, card_list, deck_code, clazzCount, rarityCount, statistic, turns, faction_win_rate, create_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql,(item['mode'], item['deck_id'], item['faction'], item['deck_name'], item['dust_cost'], item['win_rate'], item['game_count'], item['real_game_count'], item['duration'],
                                               item['background_img'], item['last_30_days'], item['card_list'], deck_code, clazzCount, rarityCount, statistic, item['turns'], item['faction_win_rate'], item['date']))
                print('insert deck', item['deck_id'], item['mode'])
        #
        # # 统计卡组名称，便于在后台进行卡组名称的翻译
        select_sql = "SELECT ename FROM winrate_decknametranslate WHERE faction=%r AND ename=%r" % (item['faction'], item['deck_name'])
        res = cursor.execute(select_sql)
        if res <= 0:
            insert_sql = """
                insert into winrate_decknametranslate(faction, ename, create_time) VALUES (%s, %s, %s)
            """
            cursor.execute(insert_sql, (item['faction'], item['deck_name'], item['date']))
        now = datetime.now().strftime(SQL_FULL_DATETIME)
        print('{0} update_decks {1}:{2}'.format(now, item['deck_name'], item['deck_id']))

    # 爬取HSReplay.net中的rank信息
    def update_rank(self, cursor, item):
        select_sql = "SELECT * FROM rank_hsranking WHERE mode=%r AND name=%r AND to_days(report_time)=to_days(now())" % (item['mode'], item['name'])
        res = cursor.execute(select_sql)
        if res > 0:
            update_sql = "update rank_hsranking set rank_no=%d, winrate=%r, report_time=%r where mode=%r AND name=%r AND to_days(report_time)=to_days(now())" \
                         % (item['rank_no'], item['winrate'], item['date'], item['mode'], item['name'])
            cursor.execute(update_sql)
        else:
            insert_sql = "insert into rank_hsranking (mode, rank_no, name, winrate, report_time) VALUES (%r, %d, %r, %r, %r)" \
                         % (item['mode'], item['rank_no'], item['name'], item['winrate'], item['date'])
            cursor.execute(insert_sql)
        print('update_rank', item['mode'], item['name'])

    # 从旅法师营地爬取所有卡牌信息
    def update_cards(self, cursor, item):
        if (item["mana"] < 0):
            return
        img = item['img'][0]
        thumbnail = item['thumbnail'][0]
        rarity = self.get_key(self.RARITY_TYPE, item['rarity'])[0]
        series_id = self.get_key(self.SERIES_TYPE, item['seriesAbbr'].upper())[0]
        clazz = self.get_key(self.CLAZZ_TYPE, item['clazz'])[0]
        if (item['standard'] == 0 and item['wild'] == 1):
            mode = 'Wild'
        elif (item['standard']):
            mode = 'Standard'
        else:
            mode = 'None'

        select_sql = "SELECT * FROM cards_cards WHERE cname=%r " % item['cname']
        res = cursor.execute(select_sql)
        if (res):
            # 数据库已有该记录则更新
            update_sql = "update cards_cards set mana=%d, hp=%d, attack=%d, description=%r, ename=%r, faction=%r, clazz=%r, race=%r, img=%r, rarity=%s, " \
                         "rule=%r, series_id=%s, mode=%r, thumbnail=%r where cname=%r" \
                         % (item['mana'], item['hp'], item['attack'], item['description'], item['ename'], item['faction'], clazz, item['race'], img, rarity, item['rule'], series_id, mode, thumbnail, item['cname'])
            cursor.execute(update_sql)
        else:
            insert_sql = """
                insert into cards_cards(mana, hp, attack, cname, description, ename, faction, clazz, race, img, rarity, rule, series_id, mode, thumbnail)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (item['mana'], item['hp'], item['attack'], item['cname'], item['description'], item['ename'], item['faction'], clazz, item['race'], img, rarity, item['rule'], series_id, mode, thumbnail))

    def update_arena_cards(self, cursor, item, spider):
        if item.get('deck_pop') <= 0.01: return
        standard_series_select_sql = "SELECT id FROM cards_series WHERE mode='Standard'"
        cursor.execute(standard_series_select_sql)
        res = cursor.fetchall()
        standard_series = []
        for set_id in res:
            standard_series.append(set_id['id'])

        select_sql = "SELECT * FROM cards_hscards WHERE dbfId=%r" % item.get('dbfId')
        res = cursor.execute(select_sql)
        if res<=0:  return
        res_card = cursor.fetchone()
        if item.get('classification') != 'ALL' and (res_card['cardClass'] != 'Neutral' and item.get('classification').upper() != res_card['cardClass'].upper()):
            return
        # 如果不是标准模式下的单卡则退出
        if res_card['set_id'] not in standard_series: return
        del res_card['id']
        del res_card['audio_play_en']
        del res_card['audio_attack_en']
        del res_card['audio_death_en']
        del res_card['audio_trigger_en']
        del res_card['audio_play_zh']
        del res_card['audio_attack_zh']
        del res_card['audio_death_zh']
        del res_card['audio_trigger_zh']
        del res_card['eflavor']
        item.update(res_card)
        # 清除item中为None的字段
        s_key = list(item.keys())
        for k_s in s_key:
            if item[k_s] is None:
                del item[k_s]
        item['update_time'] = datetime.now().strftime(SQL_FULL_DATETIME)

        tableID = spider.ifanr.tablesID['arena_cards']
        select_sql = "SELECT * FROM cards_arenacards WHERE dbfId=%r and classification=%r" % (item.get('dbfId'), item.get('classification'))
        res = cursor.execute(select_sql)
        data = item._values
        if res>0:
            self.update(cursor, item, {'dbfId': item.get('dbfId'), 'classification': item.get('classification')}, 'cards_arenacards')
            res_card = cursor.fetchone()
            spider.ifanr.put_table_data(tableID=tableID, id=res_card['ifanId'], data=data)
        else:
            self.insert(cursor, item, 'cards_arenacards')
            spider.ifanr.add_table_data(tableID=tableID, data=data)

        # tableID = spider.ifanr.tablesID['arena_cards']
        # print('ifanr query', item['classification'], item['dbfId'])
        # query = {
        #     'where': json.dumps({
        #         "$and": [
        #             {
        #                 'dbfId': {'$eq': item['dbfId']}
        #             },
        #             {
        #                 'classification': {'$eq': item['classification']}
        #             }
        #         ]
        #     }),
        # }
        # res = spider.ifanr.get_table_data(tableID=tableID, query=query)
        # data = item._values
        # if res:
        #     if (res.get('meta').get('total_count') and res.get('objects')):
        #         card = res.get('objects')[0]
        #         spider.ifanr.put_table_data(tableID=tableID, id=card['id'], data=data)
        #     else:
        #         spider.ifanr.add_table_data(tableID=tableID, data=data)
        # else:
        #     print('yf_log res is none')

# 下载图片的pipeline
class CardImagesPipeline(ImagesPipeline):
    def check_transparency(self, path):
        root, ext = os.path.splitext(path)
        return ext.index("png")

    def persist_png(self, path, data, info):
        absolute_path = self.store._get_filesystem_path(path)
        self.store._mkdir(os.path.dirname(absolute_path), info)
        f = open(absolute_path, "wb")  # use "b" to write binary data.
        f.write(data)

    def image_downloaded(self, response, request, info):
        checksum = None
        for path, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            if path.startswith("full") and self.check_transparency(path):
                # Save gif from response directly.
                self.persist_png(path, response.body, info)
            else:
                width, height = image.size
                self.store.persist_file(
                    path, buf, info,
                    meta={"width": width, "height": height},
                    headers={"Content-Type": "image/jpeg"})
        return checksum

    # 继承ImagesPipeline类，重载图片下载完之后的函数item_completed
    def item_completed(self, results, item, info):
        if "img" in item:
            for res, value in results:
                img_path = value["path"]
                item["img_path"] = img_path
        return item

    def file_path(self, request, response=None, info=None):
        img_guid = request.url.split("/")[-3]+"-"+request.url.split("/")[-1]
        return "full/%s" % (img_guid)

# 将爬取的数据导出到JSON文件，用于测试数据
class JsonExporterPipeline(object):
    # 调用scrapy提供的JsonExporter导出JSON文件
    def __init__(self):
        self.file = open('winrate.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
