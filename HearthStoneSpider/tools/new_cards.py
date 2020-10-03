from HearthStoneSpider.tools.ifan import iFanr
from scrapy.selector import Selector
from requests.auth import HTTPBasicAuth
import requests
import datetime
import time
import json

app_key = 'ca367326ae38466b9084f814274cf148'
app_secret = '3hN082V2ZSE38Ae2xtWD7V3fBH4Pukn1'

def update_new_cards_schedule():
    file = 'new_cards.html'
    with open(file, 'r', encoding='UTF-8') as f:
        text = f.read()
        t_selector = Selector(text=text)
        items = t_selector.css('div.card_revealed_item')
        ifanr = iFanr()
        tableID = ifanr.tablesID['new_cards']
        for item in items:
            cover = item.css('div.card_revealed_img img::attr(src)').extract_first('')
            u_time = item.css('div.card_revealed_time::text').extract_first('').strip()
            timestamp = int(time.mktime(time.strptime(u_time, "%Y-%m-%d %H:%M")))
            utc_reveal_time = (
                        datetime.datetime.strptime(u_time, '%Y-%m-%d %H:%M') - datetime.timedelta(hours=8)).isoformat()
            print(cover, time, utc_reveal_time)
            data = {
                'cover': cover,
                'reveal_time': timestamp
            }
            res = ifanr.add_table_data(tableID=tableID, data=data)
            print(res)

def update_new_cards(card_list):
    ifanr = iFanr()
    tableID = ifanr.tablesID['new_cards']
    file = 'new_cards.json'
    cardClassDict = {'Druid': 2, 'Hunter': 3, 'Mage': 4 , 'Paladin': 5, 'Priest': 6, 'Rogue': 7, 'Shaman': 8, 'Warlock': 9, 'Warrior': 10, 'Neutral': 12, 'DemonHunter':14}
    cardTypeDict = {'MINION': 4, 'SPELL': 5, 'HERO': 3, 'HERO_POWER': 10, 'WEAPON': 7}
    rarityDict = {'free': 2, 'common': 1, 'rare': 3, 'epic': 4, 'legendary': 5}
    raceDict = {'DRAGON': 24, 'DEMON': 15, 'PIRATE': 23, 'BEAST': 20, 'TOTEM': 21, 'MURLOC': 14, 'ELEMENTAL': 18, 'MECHANICAL': 17}
    def format_data(list):
        for item in list:
            cardClass = [k for k,v in cardClassDict.items() if v==item['classId']][0] if item.get('classId') else ''
            multiClass = []
            if item.get('multiClassIds'):
                for class_id in item.get('multiClassIds'):
                    multiClass.append([k for k,v in cardClassDict.items() if v==class_id][0])
            else:
                multiClass = [[k for k,v in cardClassDict.items() if v==item['classId']][0]] if item.get('classId') else []
            type = [k for k,v in cardTypeDict.items() if v==item['cardTypeId']][0] if item.get('cardTypeId') else ''
            rarity = [k for k,v in rarityDict.items() if v==item['rarityId']][0] if item.get('rarityId') else ''
            race = [k for k,v in raceDict.items() if v==item['minionTypeId']][0] if item.get('minionTypeId') else ''
            set_id = 26
            if item.get('cardSetId') == 1414:
                set_id = 23
            elif item.get('cardSetId') == 2:
                set_id = 1
            elif item.get('cardSetId') == 1463:
                set_id = 24
            data = {
                'name': item.get('name'),
                'dbfId': item.get('id'),
                'cost': item.get('manaCost'),
                'health': item.get('health'),
                'attack': item.get('attack'),
                'text': item.get('text'),
                'img_card_link': item.get('image'),
                'flavor': item.get('flavorText'),
                'entourage': item.get('childIds'),
                'cardClass': cardClass,
                'multiClass': multiClass,
                'collectible': item.get('collectible'),
                'artist': item.get('artistName'),
                'type': type,
                'rarity': rarity,
                'race': race,
                'set_id': set_id,
                'invalid': 0
            }
            query = {
                'where': json.dumps({
                    'dbfId': {'$eq': item['id']}
                }),
            }
            res = ifanr.get_table_data(tableID=tableID, query=query)
            if res:
                if (res.get('meta').get('total_count')):
                    card = res.get('objects')[0] if res.get('objects') else 'not found card:%s' % item['id']
                    # 首批公布的卡牌，没有发布日期则直接以当天发布的时间作为发布日期
                    # 最后一次性发布的卡，修改他的发布时间，使其显示在最前面
                    if card['created_at'] > 1596067200:
                        data['reveal_time'] = 1596067200
                    ifanr.put_table_data(tableID=tableID, id=card['id'], data=data)
                    print('update', res)
                else:
                    res = ifanr.add_table_data(tableID=tableID, data=data)
                    print('add', res)
            else:
                print('res is none')
    if card_list:
        format_data(card_list)
    else:
        with open(file, 'r', encoding='UTF-8') as f:
            list = json.load(f)
            format_data(list['cards'])

def getToken():
    auth = HTTPBasicAuth(app_key, app_secret)
    body_value = {"grant_type": "client_credentials"}
    response = requests.post(url="https://us.battle.net/oauth/token", auth=auth, data=body_value)
    re_dict = json.loads(response.text)
    return re_dict['access_token']

def getCardsList(page=1, collectible=1):
    token = getToken()
    url = 'https://us.api.blizzard.com/hearthstone/cards'
    params = {
        'locale': 'zh_CN',
        'set': 'scholomance-academy',
        'page': page,
        'collectible': collectible,
        'sort': 'name',
        'order': 'desc',
        #'class': 'demonhunter',
        'name': '鬼灵学长',
        'access_token': token
    }
    response = requests.get(url, params=params)
    res_json = json.loads(response.text)
    cards = res_json['cards']
    cardCount = res_json['cardCount']
    pageCount = res_json['pageCount']
    page = res_json['page']
    cardList.extend(cards)
    if page<pageCount:
        page += 1
        getCardsList(page=page, collectible=collectible)
    return cardList

cardList = []
if __name__ == '__main__':
    # update_new_cards_schedule()
    # update_new_cards()
    # 修改collectible=0获取衍生卡
    cardList = getCardsList(collectible=1)
    update_new_cards(cardList)