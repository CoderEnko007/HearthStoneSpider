# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don"t forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

from twisted.enterprise import adbapi
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum
from scrapy.exporters import JsonItemExporter

import MySQLdb
import MySQLdb.cursors

# class HearthstonespiderPipeline(object):
#     def process_item(self, item, spider):
#         return item

class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.RARITY_TYPE = {'1': '基本', '2': '普通', '3': '稀有', '4': '史诗', '5': '传说'}
        self.SERIES_TYPE = {'1': 'BASIC', '2': 'NAXX', '3': 'GVG', '4': 'BRM', '5': 'TGT', '6': 'LOE', '7': 'WOG',
                            '8': 'ONK', '9': 'MSG', '10': 'JUG', '11': 'KFT', '12': 'KNC', '13': 'TWW', '14': 'TBP'}
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

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        if spider.name=='HearthStone':
            query = self.dbpool.runInteraction(self.update_cards, item)
        elif spider.name=='HSReport':
            query = self.dbpool.runInteraction(self.update_rank, item)
        query.addErrback(self.handle_err)

    def handle_err(self, failure):
        # 处理异步插入的异常
        print(failure)

    # 爬取HSReplay.net中的rank信息
    def update_rank(self, cursor, item):
        print(item['date'])
        insert_sql = "insert into rank_hsranking (mode, rank_no, name, winrate, report_time) VALUES (%r, %d, %r, %r, %r)" \
                     % (item['mode'], item['rank_no'], item['name'], item['winrate'], item['date'])
        print(insert_sql)
        cursor.execute(insert_sql)

    # 从旅法师营地爬取所有卡牌信息
    def update_cards(self, cursor, item):
        if (item["mana"] < 0):
            return
        mana = item['mana']
        hp = item['hp']
        attack = item['attack']
        cname = item['cname']
        ename = item['ename']
        description = item['description']
        faction = item['faction']
        clazz = item['clazz']
        race = item['race']
        rule = item['rule']
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

        select_sql = """SELECT * FROM cards_cards WHERE cname=%r """ % cname
        res = cursor.execute(select_sql)
        if (res):
            # 数据库已有该记录则更新
            update_sql = "update cards_cards set mana=%d, hp=%d, attack=%d, description=%r, ename=%r, faction=%r, clazz=%r, race=%r, img=%r, rarity=%s, " \
                         "rule=%r, series_id=%s, mode=%r, thumbnail=%r where cname=%r" \
                         % (mana, hp, attack, description, ename, faction, clazz, race, img, rarity, rule, series_id, mode, thumbnail, cname)
            cursor.execute(update_sql)
        else:
            insert_sql = """
                insert into cards_cards(mana, hp, attack, cname, description, ename, faction, clazz, race, img, rarity, rule, series_id, mode, thumbnail)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (mana, hp, attack, cname, description, ename, faction, clazz, race, img, rarity, rule, series_id, mode, thumbnail))

class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect("127.0.0.1", "root", "", "hearthstonestation", charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.RARITY_TYPE = {'1': '基本', '2': '普通', '3': '稀有', '4': '史诗', '5': '传说'}
        self.SERIES_TYPE = {'1':'BASIC', '2':'NAXX', '3':'GVG', '4':'BRM', '5':'TGT', '6':'LOE', '7':'WOG',
                            '8':'ONK', '9':'MSG', '10':'JUG', '11':'KFT', '12':'KNC', '13':'TWW', '14':'TBP'}

    def get_key(self, dict, value):
        return [k for k, v in dict.items() if v == value]

    def process_item(self, item, spider):
        if (item["mana"] < 0):
            return
        mana = item['mana']
        hp = item['hp']
        attack = item['attack']
        cname = item['cname']
        ename = item['ename']
        description = item['description']
        faction = item['faction']
        clazz = item['clazz']
        race = item['race']
        rule = item['rule']
        img = item['img'][0]
        thumbnail = item['thumbnail'][0]

        rarity = self.get_key(self.RARITY_TYPE, item['rarity'])[0]
        series_id = self.get_key(self.SERIES_TYPE, item['seriesAbbr'].upper())[0]
        if (item['standard'] == 0 and item['wild'] == 1):
            mode = 'Wild'
        elif (item['standard']):
            mode = 'Standard'
        else:
            mode = 'None'

        try:
            select_sql = """SELECT * FROM cards_cards WHERE cname=%r """ % cname
            res = self.cursor.execute(select_sql)
            if (res):
                # 数据库已有该记录则更新
                update_sql = "update cards_cards set mana=%d, hp=%d, attack=%d, description=%r, ename=%r, faction=%r, clazz=%r, race=%r, img=%r, rarity=%s, " \
                             "rule=%r, series_id=%s, mode=%r, thumbnail=%r where cname=%r"\
                             % (mana, hp, attack, description, ename, faction, clazz, race, img, rarity, rule, series_id, mode, thumbnail, cname)
                self.cursor.execute(update_sql)
                self.conn.commit()
            else:
                insert_sql = """
                    insert into cards_cards(mana, hp, attack, cname, description, ename, faction, clazz, race, img, rarity, rule, series_id, mode, thumbnail)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(insert_sql, (mana, hp, attack, cname, description, ename, faction, clazz, race, img, rarity, rule, series_id, mode, thumbnail))
                self.conn.commit()
        except Exception as e:
            print(e)

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

class JsonExporterPipeline(object):
    # 调用scrapy提供的JsonExporter导出JSON文件
    def __init__(self):
        self.file = open('HSDecks_exporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()