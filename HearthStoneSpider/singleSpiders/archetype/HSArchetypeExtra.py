import os
import requests
from datetime import datetime
from scrapy.selector import Selector
from HearthStoneSpider.tools.dbtools import DBManager

from HearthStoneSpider.settings import SQL_FULL_DATETIME

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    files = {'One_Through_Five': 'One_Through_Five.html',
             'Legend_Only': 'Legend_Only.html'}
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
                    faction = archetype_name.split(' ')[-1]
                    win_rate = arche.css('div.archetype-data::text').extract_first('')
                    item_dict = {'tier': tier,
                                 'archetype_name': archetype_name,
                                 'faction': faction,
                                 'win_rate': float(win_rate.replace("%", "")),
                                 'rank_range': rank_range,
                                 'update_time': datetime.now().strftime(SQL_FULL_DATETIME)}
                    db = DBManager()
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