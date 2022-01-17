import os
import requests
from datetime import datetime
from scrapy.selector import Selector
from HearthStoneSpider.tools.dbtools import DBManager

from HearthStoneSpider.settings import SQL_FULL_DATETIME

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
            t_selector = Selector(text=text)
            faction_boxes = t_selector.css('div.class-box-container div.box.class-box')
            for box in faction_boxes:
                faction = box.css('div.box-title span.player-class::text').extract_first('')
                faction = faction.replace(' ', '')
                # self.faction = [faction.lower() for faction in self.faction] if self.faction else None
                # if self.faction and faction.lower() not in self.faction:
                #     continue
                archetype_list = box.css('div.grid-container')[2].css('a.player-class::text').extract()
                archetype_list_other_item = box.css('div.grid-container')[2].css('span.player-class div.tooltip-wrapper::text').extract_first('')
                if archetype_list_other_item != '':
                    archetype_list.append(archetype_list_other_item)
                data_cells = box.css('div.grid-container')[3].css('.table-cell::text').extract()
                data_list = []
                list_temp = []
                for item in data_cells:
                    list_temp.append(item)
                    if len(list_temp) % 3 == 0:
                        data_list.append(list_temp)
                        list_temp = []
                        continue
                for i, archetype in enumerate(archetype_list):
                    try:
                        item_dict = {
                            'rank_range': rank_range,
                            'faction': faction,
                            'archetype': archetype,
                            'winrate': float(data_list[i][0].replace("%", "")),
                            'popularity': float(data_list[i][1].replace("%", "")),
                            'games': int(data_list[i][2].replace(',', '')),
                            'create_time': datetime.now().strftime(SQL_FULL_DATETIME)
                        }
                    except Exception as e:
                        print(e)
                        print(i, archetype, data_list)
                    print(item_dict)
                    select_sql = "SELECT * FROM winrate_hswinrate WHERE faction=%r AND rank_range=%r AND archetype=%r AND to_days(create_time)=to_days(now())" \
                                 % (item_dict['faction'], item_dict['rank_range'], item_dict['archetype'])
                    res = db.cursor.execute(select_sql)
                    res_item = db.cursor.fetchone()
                    if res>0:
                        db.update('winrate_hswinrate', item_dict, {'id': res_item.get('id')})
                        print('update', item_dict)
                    else:
                        db.insert('winrate_hswinrate', item_dict)
                        print('insert', item_dict)
    requests.get('https://cloud.minapp.com/oserve/v1/incoming-webhook/elzp6Ttp2L')