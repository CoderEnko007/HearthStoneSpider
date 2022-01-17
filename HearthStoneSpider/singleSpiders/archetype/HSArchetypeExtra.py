import os
import requests
from datetime import datetime
from scrapy.selector import Selector
from HearthStoneSpider.tools.dbtools import DBManager

from HearthStoneSpider.settings import SQL_FULL_DATETIME

# class


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    files = {'BRONZE_THROUGH_GOLD': 'Bronze_through_Gold.html',
             'DIAMOND_FOUR_THROUGH_DIAMOND_ONE': 'Diamond_4_1.html',
             'DIAMOND_THROUGH_LEGEND': 'Diamond_through_Legend.html',
             'LEGEND': 'Legend.html',
             'TOP_1000_LEGEND': 'Legend_top_1000.html'
             }
    db = DBManager()
    for range, file in files.items():
        file_name = os.path.join(BASE_DIR, file)
        with open(file_name, 'r', encoding='UTF-8') as f:
            rank_range = range
            text = f.read()
            # print(text)
            t_selector = Selector(text=text)
            archetype_tier = t_selector.css('div.archetype-tier-list div.tier')
            for item in archetype_tier:
                tier = item.css('div.tier-header::text').extract_first('')
                archetype_list_items = item.css('li.archetype-list-item')
                for arche in archetype_list_items:
                    archetype_name = arche.css('div.archetype-name::text').extract_first('')
                    faction = archetype_name.split(' ')
                    if len(faction) > 2 and faction[-2].lower() == 'demon':
                        faction = 'DemonHunter'
                    else:
                        faction = faction[-1]
                        if faction == 'Handlock':
                            faction = 'Warlock'
                    win_rate = arche.css('div.archetype-data::text').extract_first('')

                    select_sql = "SELECT popularity, games FROM winrate_hswinrate WHERE faction=%r AND rank_range=%r AND archetype=%r AND to_days(create_time)=to_days(now())" \
                                 % (faction, rank_range, archetype_name)
                    res = db.cursor.execute(select_sql)
                    if res > 0:
                        res_deck = db.cursor.fetchone()
                        popularity1 = float(res_deck.get('popularity'))
                        game_count = int(res_deck.get('games'))
                    else:
                        popularity1 = 0
                        game_count = 0

                    item_dict = {'tier': tier,
                                 'archetype_name': archetype_name,
                                 'faction': faction,
                                 'win_rate': float(win_rate.replace("%", "")),
                                 'popularity1': popularity1,
                                 'game_count': game_count,
                                 'rank_range': rank_range,
                                 'update_time': datetime.now().strftime(SQL_FULL_DATETIME)}
                    select_sql = "SELECT * FROM archetype_archetype WHERE archetype_name=%r AND rank_range=%r AND to_days(update_time)=to_days(now())" % \
                                 (archetype_name, rank_range)
                    res = db.cursor.execute(select_sql)
                    res_item = db.cursor.fetchone()
                    if res>0:
                        db.update('archetype_archetype', item_dict, {'id': res_item.get('id')})
                        print('update', item_dict)
                    else:
                        db.insert('archetype_archetype', item_dict)
                        print('insert', item_dict)
    requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/RGFLY7CmCp')