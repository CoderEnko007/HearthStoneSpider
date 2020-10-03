import re
import json
import platform
from datetime import datetime
from HearthStoneSpider.tools.remote_server import HSServer
from HearthStoneSpider.settings import SQL_DATETIME_FORMAT

def update_winrate(self, cursor, item):
    data = dict(item, **{
        'create_time': item['date']
    })
    del data['date']

    if platform.platform().find('Windows') != -1:
        # 本地更新
        local_update(cursor, data)
    else:
        # 服务器更新
        remote_update(self, cursor, item)

def format_cards_list(cursor, cards_list):
    for cards in cards_list:
        for card in cards:
            select_sql = "SELECT dbfId, rarity, name, img_tile_link FROM cards_hscards WHERE hsId=%r" % card['card_hsid']
            cursor.execute(select_sql)
            res_card = cursor.fetchone()
            try:
                card.update({'dbfId': res_card.get('dbfId')})
                card.update({'rarity': res_card.get('rarity')})
                card.update({'cname': res_card.get('name')})
                if res_card.get('img_tile_link'):
                    tile = re.match('^.*\/(.*\.png)', res_card.get('img_tile_link'))
                    tile = tile.group(1) if tile is not None else ''
                    card.update({'tile': tile})
                else:
                    card.update({'tile': ''})
            except Exception as e:
                print('update card error:', e, card)
    return cards_list

def local_update(cursor, data):
    server = HSServer('winrate/')
    if data['rank_range'] == 'BRONZE_THROUGH_GOLD':
        core_cards = data.get('core_cards')
        pop_cards = data.get('pop_cards')
        if data['archetype'] != 'Other':
            format_list = format_cards_list(cursor, [core_cards, pop_cards])
            data['core_cards'] = json.dumps(format_list[0], ensure_ascii=False)
            data['pop_cards'] = json.dumps(format_list[1], ensure_ascii=False)
    params = {
        'rank_range': data['rank_range'],
        'faction': data['faction'],
        'archetype': data['archetype'],
        'create_time': datetime.now().strftime(SQL_DATETIME_FORMAT)
    }
    print('params', params)
    res = server.list(params=params)
    if res['status_code'] == 200 and res['count'] > 0:
        id = res['results'][0].get('id')
        res = server.put(id=id, data=data)
    else:
        res = server.post(data=data)
    print('aaa', res)

def remote_update(self, cursor, data):
    if data['rank_range'] != 'BRONZE_THROUGH_GOLD':
        select_sql = "SELECT id FROM winrate_hswinrate WHERE faction=%r AND rank_range=%r AND archetype=%r AND to_days(create_time)=to_days(now())" \
                     % (data['faction'], data['rank_range'], data['archetype'])
        res = cursor.execute(select_sql)
        if res > 0:
            res_item = cursor.fetchone()
            self.update(cursor, data, {'id': res_item.get('id')}, 'winrate_hswinrate')
            print('update', data)
        else:
            self.insert(cursor, data, 'winrate_hswinrate')
            print('insert', data)
    else:
        if data['archetype'] != 'Other':
            core_cards = data.get('core_cards')
            pop_cards = data.get('pop_cards')
            format_list = format_cards_list(cursor, [core_cards, pop_cards])
            data['core_cards'] = json.dumps(format_list[0], ensure_ascii=False)
            data['pop_cards'] = json.dumps(format_list[1], ensure_ascii=False)
        select_sql = "SELECT id FROM winrate_hswinrate WHERE faction=%r AND rank_range=%r AND archetype=%r AND to_days(create_time)=to_days(now())" \
                     % (data['faction'], data['rank_range'], data['archetype'])
        res = cursor.execute(select_sql)
        if res > 0:
            res_arche = cursor.fetchone()
            if data['archetype'] != 'Other':
                update_sql = "update winrate_hswinrate set winrate=%f, popularity=%f, games=%d, faction_popularity=%f, real_winrate=%f, real_games=%d, best_matchup=%r, worst_matchup=%r," \
                             "pop_deck=%r, best_deck=%r, core_cards=%r, pop_cards=%r, matchup=%r, create_time=%r where id=%r" \
                             % (data['winrate'], data['popularity'], data['games'], data['faction_popularity'],
                                data['real_winrate'], data['real_games'], data['best_matchup'], data['worst_matchup'],
                                data['pop_deck'], data['best_deck'], data['core_cards'], data['pop_cards'],
                                data['matchup'], data['create_time'], res_arche['id'])
            else:
                update_sql = "update winrate_hswinrate set winrate=%f, popularity=%f, games=%d, create_time=%r where id=%r" \
                             % (data['winrate'], data['popularity'], data['games'], data['create_time'], res_arche['id'])
            print('测试: update ', data['archetype'], update_sql)
            cursor.execute(update_sql)
        else:
            if data['archetype'] != 'Other':
                insert_sql = """
                       insert into winrate_hswinrate(rank_range, faction, archetype, winrate, popularity, games, faction_popularity, real_winrate, real_games, best_matchup, worst_matchup, pop_deck, best_deck, core_cards, pop_cards, matchup, create_time)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   """
                cursor.execute(insert_sql, (
                    data['rank_range'], data['faction'], data['archetype'], data['winrate'], data['popularity'],
                    data['games'], data['faction_popularity'], data['real_winrate'], data['real_games'],
                    data['best_matchup'], data['worst_matchup'], data['pop_deck'], data['best_deck'],
                    data['core_cards'], data['pop_cards'], data['matchup'], data['create_time']))
            else:
                insert_sql = """
                       insert into winrate_hswinrate(rank_range, faction, archetype, winrate, popularity, games, create_time)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                   """
                cursor.execute(insert_sql, (
                    data['rank_range'], data['faction'], data['archetype'], data['winrate'], data['popularity'],
                    data['games'], data['create_time']))
            print('测试: insert ', data['archetype'])