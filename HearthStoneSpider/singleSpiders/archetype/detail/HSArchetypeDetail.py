import os
import re
import json
from datetime import datetime
from scrapy.selector import Selector
from HearthStoneSpider.tools.dbtools import DBManager

from HearthStoneSpider.settings import SQL_DATETIME_FORMAT, SQL_FULL_DATETIME
from HearthStoneSpider.module.HSWinRateModule import update_winrate, local_update

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    overview_file = 'overview.html'
    matchup_file = 'matchup.html'
    default_rank_range = 'BRONZE_THROUGH_GOLD'
    db = DBManager()
    with open(overview_file, 'r', encoding='UTF-8') as f:
        text = f.read()
        t_selector = Selector(text=text)
        archetype = t_selector.css('div.archetype-image-container h1::text').extract_first('')
        faction = 'DemonHunter' if 'Demon Hunter' in archetype else archetype.split(' ')[-1]
        rank_range = default_rank_range
        real_win_rate = t_selector.css('a.winrate-box .box-content h1::text').extract_first('')
        real_win_rate = re.findall('\d+', real_win_rate)
        real_win_rate = '.'.join(real_win_rate)
        # winrate = real_win_rate

        real_game_count = t_selector.css('a.winrate-box .box-content h3::text').extract_first('')
        real_game_count = re.findall('\d+', real_game_count)
        real_game_count = int(''.join(real_game_count))
        # game = real_game_count

        faction_popularity = t_selector.css('a.popularity-box .box-content h1::text').extract_first('')
        faction_popularity = re.findall('\d+', faction_popularity)
        try:
            faction_popularity = float('.'.join(faction_popularity))
        except Exception as e:
            faction_popularity = 0

        deck_box = t_selector.css('a.deck-box')
        if len(deck_box) > 0:
            pop_deck_code = t_selector.css('a.deck-box::attr(href)').extract()
            if pop_deck_code:
                pop_deck_code = pop_deck_code[0]
                pop_deck_code = re.match('.*\/(.*)\/', pop_deck_code).group(1)
                pop_deck_win_rate = deck_box[0].css('div.stats-table tr')[0].css('td::text').extract_first('')
                pop_deck_games = deck_box[0].css('div.stats-table tr')[1].css('td::text').extract_first('')
                pop_deck = [pop_deck_code, pop_deck_win_rate, pop_deck_games]
            else:
                pop_deck = []
        else:
            pop_deck = []
        pop_deck = json.dumps(pop_deck, ensure_ascii=False)

        if len(deck_box) > 1:
            best_deck_code = t_selector.css('a.deck-box::attr(href)').extract()
            if best_deck_code:
                best_deck_code = best_deck_code[1]
                best_deck_code = re.match('.*\/(.*)\/', best_deck_code).group(1)
                best_deck_win_rate = deck_box[1].css('div.stats-table tr')[0].css('td::text').extract_first('')
                best_deck_games = deck_box[1].css('div.stats-table tr')[1].css('td::text').extract_first('')
                best_deck = [best_deck_code, best_deck_win_rate, best_deck_games]
            else:
                best_deck = []
        else:
            best_deck = []
        best_deck = json.dumps(best_deck, ensure_ascii=False)

        matchup_box = t_selector.css('a.matchup-box')
        if len(matchup_box) > 0:
            best_matchup_player_class = matchup_box[0].css('span.player-class::text').extract_first('')
            best_matchup_faction = matchup_box[0].css('span.player-class::attr(class)').extract_first('')
            best_matchup_faction = best_matchup_faction.split(' ')[-1].capitalize()
            if best_matchup_faction == 'Demonhunter':
                best_matchup_faction = 'DemonHunter'
            matchup_box_tr = matchup_box[0].css('div.stats-table tr')
            if len(matchup_box_tr) > 1:
                best_matchup_win_rate = matchup_box_tr[0].css('td::text').extract_first('')
                best_matchup_games = matchup_box_tr[1].css('td::text').extract_first('')
                best_matchup = [best_matchup_player_class, best_matchup_win_rate, best_matchup_games, best_matchup_faction]
            else:
                best_matchup = []
        else:
            best_matchup = []
        best_matchup = json.dumps(best_matchup, ensure_ascii=False)

        if len(matchup_box) > 1:
            worst_matchup_player_class = matchup_box[1].css('span.player-class::text').extract_first('')
            worst_matchup_faction_t = matchup_box[1].css('span.player-class::attr(class)').extract_first('')
            worst_matchup_faction = worst_matchup_faction_t.split(' ')[-1].capitalize()
            if worst_matchup_faction == 'Demonhunter':
                worst_matchup_faction = 'DemonHunter'
            matchup_box_tr = matchup_box[1].css('div.stats-table tr')
            if len(matchup_box_tr) > 1:
                worst_matchup_win_rate = matchup_box[1].css('div.stats-table tr')[0].css('td::text').extract_first('')
                worst_matchup_games = matchup_box[1].css('div.stats-table tr')[1].css('td::text').extract_first('')
                worst_matchup = [worst_matchup_player_class, worst_matchup_win_rate, worst_matchup_games, worst_matchup_faction]
            else:
                print('yf_log: worst_matchup matchup_box_tr is null ')
                worst_matchup = []
        else:
            print('yf_log: worst_matchup matchup_box is null')
            worst_matchup = []
        worst_matchup = json.dumps(worst_matchup, ensure_ascii=False)

        card_list_wrapper = t_selector.css('div.archetype-signature div.card-list-wrapper')
        core_card_list_items = card_list_wrapper[0].css('.card-tile') if len(card_list_wrapper) > 0 else []
        core_cards = []
        for item in core_card_list_items:
            card_name = item.css('.card-name::text').extract_first('')
            card_cost = item.css('.card-cost::text').extract_first('')
            card_assert = item.css('img.card-asset::attr(src)').extract_first('')
            card_hsid = card_assert.split('/')[-1].split('.')[0]
            # core_cards.append([card_name, card_cost, card_assert])
            core_cards.append({'name': card_name, 'cost': card_cost, 'card_hsid': card_hsid})

        pop_card_list_items = card_list_wrapper[1].css('.card-tile') if len(card_list_wrapper) > 1 else []
        pop_cards = []
        for item in pop_card_list_items:
            card_name = item.css('.card-name::text').extract_first('')
            card_cost = item.css('.card-cost::text').extract_first('')
            card_assert = item.css('img.card-asset::attr(src)').extract_first('')
            card_hsid = card_assert.split('/')[-1].split('.')[0]
            # pop_cards.append([card_name, card_cost, card_assert])
            pop_cards.append({'name': card_name, 'cost': card_cost, 'card_hsid': card_hsid})

    item_dict = {'faction': faction,
             'rank_range': rank_range,
             'archetype': archetype,
             'faction_popularity': faction_popularity,
             'real_winrate': real_win_rate,
             'real_games': real_game_count,
             'best_matchup': best_matchup,
             'worst_matchup': worst_matchup,
             'pop_deck': pop_deck,
             'best_deck': best_deck,
             'core_cards': core_cards,
             'pop_cards': pop_cards}
    #
    #   matchup detail
    #
    with open(matchup_file, 'r', encoding='UTF-8') as f:
        text = f.read()
        t_selector = Selector(text=text)
        faction_boxes = t_selector.css('div.class-box-container div.box.class-box')
        matchup = {'Druid': [], 'Hunter': [], 'Mage': [], 'Paladin': [], 'Priest': [], 'Rogue': [], 'Shaman': [],
                   'Warlock': [], 'Warrior': [], 'DemonHunter': []}
        for box in faction_boxes:
            faction = box.css('div.box-title span.player-class::text').extract_first('').replace(' ', '')
            archetype_list = box.css('div.grid-container')[2].css('a.player-class::text').extract()
            data_cells = box.css('div.grid-container')[3].css('a.table-cell::text').extract()
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
                    data_list[i].insert(0, archetype)
                except Exception as e:
                    print(e, data_list, archetype_list)
            # matchup.append(data_list)
            matchup[faction] = data_list
        matchup = json.dumps(list(matchup.values()), ensure_ascii=False)
    item_dict.update({'matchup': matchup})

    #
    # winrate meta data
    #
    select_sql = "SELECT winrate, popularity, games FROM winrate_hswinrate WHERE faction=%r AND rank_range=%r AND archetype=%r AND to_days(create_time)=to_days(now())" \
                 % (faction, rank_range, archetype)
    res = db.cursor.execute(select_sql)
    if res > 0:
        res_deck = db.cursor.fetchone()
        winrate = float(res_deck.get('winrate'))
        popularity = float(res_deck.get('popularity'))
        games = int(res_deck.get('games'))
    else:
        winrate = 0
        popularity = 0
        games = 0
    item_dict.update({'winrate': winrate, 'popularity': popularity, 'games': games,
                      'create_time': datetime.now().strftime(SQL_FULL_DATETIME)})

    local_update(db.cursor, item_dict)
    pass