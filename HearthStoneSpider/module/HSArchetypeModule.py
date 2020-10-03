import re
import json
import platform
import requests
from datetime import datetime
from HearthStoneSpider.tools.remote_server import HSServer
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME

def update_archetype(self, cursor, item, spider):
    item['core_cards'] = '[]'
    item['pop_cards'] = '[]'
    item['date'] = datetime.now().strftime(SQL_FULL_DATETIME)
    data = dict(item, **{
        'update_time': item['date']
    })
    del data['date']

    if platform.platform().find('Windows') != -1:
        # 本地更新
        local_update(data)
    else:
        # 服务器更新
        remote_update(self, cursor, data, spider)

def local_update(data):
    server = HSServer()
    server.set_url_path('winrate/')
    pop_query_params = {
        'faction': data['faction'],
        'rank_range': data['rank_range'],
        'archetype': data['archetype_name'],
        'create_time': datetime.now().strftime(SQL_DATETIME_FORMAT)
    }
    res = server.list(params=pop_query_params)
    if res['status_code'] == 200 and res['count'] > 0:
        data['popularity1'] = float(res['results'][0].get('popularity'))
    else:
        data['popularity1'] = 0

    server.set_url_path('archetype/')
    params = {
        'rank_range': data['rank_range'],
        'archetype_name': data['archetype_name'],
        'update_time': datetime.now().strftime(SQL_DATETIME_FORMAT)
    }
    print('params', params)
    res = server.list(params=params)
    if res['status_code'] == 200 and res['count'] > 0:
        id = res['results'][0].get('id')
        res = server.put(id=id, data=data)
    else:
        res = server.post(data=data)
    print('aaa', res)

def remote_update(self, cursor, item, spider):
    select_sql = "SELECT popularity FROM winrate_hswinrate WHERE faction=%r AND rank_range=%r AND archetype=%r AND to_days(create_time)=to_days(now())" \
                 % (item['faction'], item['rank_range'], item['archetype_name'])
    res = cursor.execute(select_sql)
    if res > 0:
        res_deck = cursor.fetchone()
        popularity1 = float(res_deck.get('popularity'))
    else:
        popularity1 = 0

    select_sql = "SELECT id FROM archetype_archetype WHERE archetype_name=%r AND rank_range=%r AND to_days(update_time)=to_days(now())" % (
        item['archetype_name'], item['rank_range'])
    res = cursor.execute(select_sql)
    if res > 0:
        res_item = cursor.fetchone()
        data = dict(item, **{
            'popularity1': popularity1
        })
        self.update(cursor, data, {'id': res_item.get('id')}, 'archetype_archetype')
    else:
        insert_sql = """
                insert into archetype_archetype(rank_range, tier, faction, archetype_name, win_rate, game_count, popularity, popularity1, best_matchup, worst_matchup, pop_deck, best_deck, core_cards, pop_cards, matchup, update_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        cursor.execute(insert_sql, (
            item['rank_range'], item['tier'], item['faction'], item['archetype_name'], item['win_rate'], item['game_count'],
            item['popularity'], popularity1, item['best_matchup'], item['worst_matchup'], item['pop_deck'], item['best_deck'], item['core_cards'],
            item['pop_cards'], item['matchup'], item['update_time']))
    archetypes_counts = spider.crawler.stats.get_value('archetypes_counts')
    spider.saved_count += 1
    print('update archetype', item['rank_range'], item['archetype_name'], archetypes_counts, spider.saved_count)
    if (spider.saved_count == archetypes_counts):
        requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/RGFLY7CmCp')  # HSArchetypeRangeDataWebHook
        print('update archetype end, up to ifanr')