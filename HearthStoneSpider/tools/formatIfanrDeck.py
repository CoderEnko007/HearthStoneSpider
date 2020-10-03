from HearthStoneSpider.tools.ifan import iFanr
import json
import time

def filter_decks(ifanr, query, query_card=None, limit=20, page=0, offset=0):
    tableID = ifanr.tablesID['winrate']
    query_ = dict(query, **{
        'limit': limit,
        'offset': offset
    })
    res = ifanr.get_table_data(tableID=tableID, query=query_)
    check_card_list = [
        {'dbfId':56622, 'cost':7},
        {'dbfId':55421, 'cost':4},
        {'dbfId':56652, 'cost':4},
        {'dbfId':41872, 'cost':4},
        {'dbfId':56394, 'cost':5}]
    if len(res.get('objects')):
        for deck in res.get('objects'):
            # 修改faction_win_Rate中恶魔猎手职业的英文单词，统一为DemonHunter
            # print(deck.get('faction_win_rate').find('Demonhunter'))
            # if deck.get('faction_win_rate').find('Demonhunter')!=-1:
            #     deck['faction_win_rate'] = deck['faction_win_rate'].replace('Demonhunter', 'DemonHunter')
            #     response = ifanr.put_table_data(tableID=tableID, id=deck['_id'], data=deck)
            #     re_dict = json.loads(response.text)
            #     print('update', re_dict)
            card_list = json.loads(deck.get('card_list'))
            upgrade_flag = False
            if query_card != None:
                for card in card_list:
                    for check_card in check_card_list:
                        if card['dbfId'] == check_card['dbfId']:
                            card['cost'] = check_card['cost']
                            upgrade_flag = True
                if upgrade_flag:
                    deck['card_list'] = json.dumps(card_list)
                    response = ifanr.put_table_data(tableID=tableID, id=deck['_id'], data=deck)
                    re_dict = json.loads(response.text)
                    print('update', re_dict)
            else:
                print('请传入需要筛选卡牌的dbfid')
            pass
    if res.get('meta').get('next'):
        page += 1
        filter_decks(ifanr, query, query_card=query_card, limit=20, page=page, offset=limit*page)
    pass

if __name__ == '__main__':
    ifanr = iFanr()
    dt = '2020-04-10 00:00:00'
    ts = int(time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S")))
    query_card = [56394]
    query = {
        'where': json.dumps({
            # 'last_30_days': {'$eq': False},
            # 'updated_at': {'$gt': ts},
            'card_array': {'$in': query_card}
        }),
    }
    filter_decks(ifanr, query, query_card)