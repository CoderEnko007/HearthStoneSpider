document.addEventListener('DOMContentLoaded', async function() {
    console.log('content-script:', location)
    // sleep(1000)
    // 这里好像会影响popup接收的消息
    var current_mode = await asyncSendMessageToBackground({msg:MSG_ID.MSG_GET_CURRENT_MODE, payload: null})
    console.log('当前脚本模式current_mode:', current_mode)
    if (current_mode.payload == MODE_ID.MODE_NONE) return
    var href = location.href
    var hash = location.hash
    var pathname = location.pathname
    console.log('=============DOMContentLoaded=============')
    var decks_reg = /\/decks\/(.*)\//
    var deck_detail_flag = decks_reg.test(pathname)
    var archetype_reg = /\/archetypes\/(.*)\//
    var archetype_detail_flag = archetype_reg.test(pathname)
    console.log(hash, pathname, pathname.split('/').indexOf('decks'))
    if (deck_detail_flag && hash.length && (pathname&&pathname.split('/').indexOf('decks')>0)) {
        var timer_times = 0
        var timer = window.setInterval(function() {
            sleep(1000)
            var overview_block = document.querySelectorAll('table.table-striped tbody tr')
            var deck_name = document.querySelector('.archetype-image-container h1')
            var wild_flag = hash.indexOf('RANKED_WILD')>0
            var classic_flag = hash.indexOf('RANKED_CLASSIC')>0
            timer_times += 1
            console.log('debug:', wild_flag, deck_name||wild_flag||classic_flag, overview_block.length&&(deck_name||wild_flag))
            if ((overview_block.length&&(deck_name||wild_flag||classic_flag)) || timer_times >= 15) {
                clearInterval(timer)
                var deck_id = location.pathname.match(/\/.*\/(.*)\//)[1]

                var deck_name = document.querySelector('.archetype-image-container h1')
                if (deck_name) {
                    deck_name = deck_name.textContent
                } else {
                    // deck_name = ''
                    var deck_info_block = document.querySelector('#deck-info')
                    deck_name = deck_info_block.getAttribute('data-deck-name')
                    deck_name = deck_name.split(' ')[0]
                }

                var real_game_count = document.querySelectorAll('.infobox section ul span.infobox-value')
                if (real_game_count.length && real_game_count[0].textContent) {
                    real_game_count = parseInt(real_game_count[0].textContent.replace(',', ''))
                } else {
                    real_game_count = 0
                }

                var card_list_items = document.querySelectorAll('#overview .card-list-wrapper .card-list .tooltip-wrapper .card-tile')
                var card_list = []
                for(var item of card_list_items) {
                    var card_cost = parseInt(item.querySelector('span.card-cost').textContent)
                    var card_asset = item.querySelector('div.card-frame img.card-asset').getAttribute('src')
                    var card_hsid = card_asset.match(/.*\/(.*)\.[a-zA-Z]*$/)[1]
                    var card_count_cell = item.querySelector('.card-count')
                    var card_count = card_count_cell?card_count_cell.textContent:1
                    card_count = isNaN(card_count)?1:parseInt(card_count)
                    var card_name = item.querySelector('.card-name').textContent
                    card_list.push({'name': card_name, 'cost': card_cost, 'count': card_count, 'card_hsid': card_hsid})
                }

                var table_field = document.querySelectorAll('table.table-striped tbody tr')
                var turns = 0
                var duration = 0
                if (table_field.length) {
                    turns = table_field[1].querySelectorAll('td')[1].textContent
                    turns = parseFloat(turns)
                    duration = table_field[0].querySelectorAll('td')[1].textContent
                    duration = parseFloat(duration)
                }

                var win_rate_cell = document.querySelector('table.table-striped tbody tr td.winrate-cell')
                var real_win_rate = 0
                if(win_rate_cell) {
                    real_win_rate = parseFloat(win_rate_cell.textContent.replace('%', ''))
                }

                var win_rate_nodes = document.querySelectorAll('table.table-striped tbody tr')
                var faction_win_rate = []
                if (win_rate_nodes.length) {
                    for(var i=4; i<win_rate_nodes.length; i++) {
                        var item = win_rate_nodes[i]
                        var faction_str = item.querySelector('td span.player-class').getAttribute('class')
                        var faction = faction_str.match(/.* (\w*)$/)[1]
                        if(faction.toUpperCase() === 'DEMONHUNTER') {
                            faction = 'DemonHunter'
                        } else {
                            faction = firstUpperCase(faction)
                        }
                        var win_rate = item.querySelector('td.winrate-cell').textContent
                        win_rate = parseFloat(win_rate.replace(/[^0-9.]/ig,""))
                        faction_win_rate.push({'faction': faction, 'win_rate': win_rate})
                    }
                }
                faction_win_rate = JSON.stringify(faction_win_rate)

                var dust_cost_field = document.querySelectorAll('.infobox ul li .infobox-value')
                var dust_cost = 0
                if (dust_cost_field.length) {
                    for(var item of dust_cost_field) {
                        if (item.textContent.indexOf('Dust')>0) {
                            dust_cost = parseInt(item.textContent)
                        }
                    }
                }

                var mulligan_block = document.querySelector('#tab-mulligan-guide')
                var mulligan_flag = mulligan_block?true:false
                // var rank_mode = hash.indexOf('RANKED_WILD')>=0?'Wild':'Standard'
                var rank_mode = 'Standard'
                if (hash.indexOf('RANKED_WILD')>=0) {
                    rank_mode = 'Wild'
                } else if (hash.indexOf('RANKED_CLASSIC')>=0) {
                    rank_mode = 'Classic'
                }
                var deck = {
                    deck_id: deck_id,
                    deck_name: deck_name,
                    real_game_count: real_game_count,
                    card_list: card_list,
                    turns: turns,
                    real_win_rate: real_win_rate,
                    faction_win_rate: faction_win_rate,
                    mode: rank_mode,
                    mulligan_flag: mulligan_flag,
                    dust_cost: dust_cost,
                    duration: duration,
                    last_30_days: false
                }
                if(mulligan_flag) {
                    console.log('点击调度建议按钮')
                    mulligan_block.click()
                    console.log('点击调度建议按钮完成')
                    var mulligan_timer_times = 0
                    var mulligan_timer = window.setInterval(function() {
                        var mulligan_guide = document.querySelector('#mulligan-guide .table-container')
                        console.log('检查mulligan是否存在：', timer_times, mulligan_guide, deck)
                        mulligan_timer_times += 1
                        if (mulligan_guide || mulligan_timer_times >= 10) {
                            clearInterval(mulligan_timer)
                            var mulligan_flag = mulligan_guide?true:false
                            console.log('查询调度建议表格是否存在', mulligan_guide, mulligan_flag)
                            deck.mulligan_flag = mulligan_flag
                            sendMessageToBackground({msg: BG_MSG_ID.MSG_UPDATE_DECK, payload: deck})
                        }
                    }, 2000, deck)
                } else {
                    sendMessageToBackground({msg: BG_MSG_ID.MSG_UPDATE_DECK, payload: deck})
                }
            }
            console.log('定时器次数：', timer_times, deck)
        }, 2000)
    } else if (pathname === '/analytics/query/single_deck_mulligan_guide_v2/') {
        var deck_id = href.match(/.*deck_id=([0-9A-Za-z]*).*$/)[1]
        console.log('mulligan_guide deck_id:', deck_id)
        var mulligan_block = document.querySelector('pre')
        var mulligan = []
        if (mulligan_block) {
            mulligan = JSON.parse(mulligan_block.textContent)
            mulligan = mulligan.series.data.ALL
            for (var item of mulligan) {
                for (var key in item) {
                    if (!item[key]) {
                        item[key]=0
                    }
                }
            }
        }
        var deck = {
            deck_id: deck_id,
            mulligan: mulligan
        }
        console.log('content-script解析mulligan完毕', mulligan)
        sendMessageToBackground({msg: BG_MSG_ID.MSG_HANDLE_MULLIGAN, payload: deck})
    } else if (archetype_detail_flag) {
        // 解析卡组模板页面
        var timer_times = 0
        var timer = window.setInterval(function() {
            var name_block = document.querySelector('.archetype-image-container h1')
            var winrate_block = document.querySelector('a.winrate-box .box-content')
            var winrate_block_flag = winrate_block && winrate_block.textContent.length>0
            // var real_games_block = document.querySelector('a.winrate-box .box-content h3')
            var popularity_block = document.querySelector('a.popularity-box .box-content')
            var popularity_block_flag = popularity_block && popularity_block.textContent.length>0
            var deck_block = document.querySelectorAll('a.deck-box .box-content')
            var deck_block_flag = deck_block.length>1 && deck_block[0].textContent.length>0 && deck_block[1].textContent.length>0
            var matchup_block = document.querySelectorAll('a.matchup-box .box-content')
            var matchup_block_flag = matchup_block.length>1 && matchup_block[0].textContent.length && matchup_block[1].textContent.length
            var archetype_block = document.querySelector('.archetype-signature')
            console.log('aaa', name_block, name_block.textContent)
            if (((name_block&&name_block.textContent) && winrate_block_flag && popularity_block_flag && popularity_block && deck_block_flag
                 && matchup_block_flag && archetype_block && timer_times>0) || timer_times>15) {
                clearInterval(timer)
                var archetype = {}
                var faction = firstUpperCase(document.querySelector('#archetype-container').getAttribute('data-archetype-player-class'))
                archetype['faction'] = faction=='Demonhunter'?'DemonHunter':faction
                archetype['archetype'] = name_block.textContent
                var winrate = winrate_block.querySelector('h1')
                if (winrate) {
                    archetype['real_winrate'] = parseFloat(winrate.textContent.replace('%', ''))
                } else {
                    archetype['real_winrate'] = 0
                }
                var real_games = winrate_block.querySelector('h3')
                if (real_games) {
                    archetype['real_games'] = parseInt(real_games.textContent.replace(/[^0-9]/ig,""))
                } else {
                    archetype['real_games'] = 0
                }
                var popularity = popularity_block.querySelector('h1')
                if (popularity) {
                    archetype['faction_popularity'] = parseFloat(popularity.textContent.replace('%', ''))
                } else {
                    archetype['faction_popularity'] = 0
                }
                archetype['best_matchup'] = '[]'
                archetype['worst_matchup'] = '[]'
                archetype['pop_deck'] = '[]'
                archetype['best_deck'] = '[]'
                if (matchup_block.length>1) {
                    if (matchup_block[0].querySelector('span.player-class') && matchup_block[0].querySelectorAll('div.stats-table tr')) {
                        var best_matchup_player_class = matchup_block[0].querySelector('span.player-class').textContent
                        var best_matchup_faction = matchup_block[0].querySelector('span.player-class').getAttribute('class').split(' ')[1]
                        best_matchup_faction = firstUpperCase(best_matchup_faction)
                        if (best_matchup_faction == 'Demonhunter') {
                            best_matchup_faction = 'DemonHunter'
                        }
                        var matchup_box_tr = matchup_block[0].querySelectorAll('div.stats-table tr')
                        if (matchup_box_tr.length > 1) {
                            var best_matchup_win_rate = matchup_box_tr[0].querySelector('td').textContent
                            var best_matchup_games = matchup_box_tr[1].querySelector('td').textContent
                            archetype['best_matchup'] = JSON.stringify([best_matchup_player_class, best_matchup_win_rate, best_matchup_games, best_matchup_faction])
                        }
                    } else {
                        console.log('best match up为空')
                    }
                    if (matchup_block[1].querySelector('span.player-class') && matchup_block[1].querySelectorAll('div.stats-table tr')) {
                        var worst_matchup_player_class = matchup_block[1].querySelector('span.player-class').textContent
                        var worst_matchup_faction = matchup_block[1].querySelector('span.player-class').getAttribute('class').split(' ')[1]
                        worst_matchup_faction = firstUpperCase(worst_matchup_faction)
                        if (worst_matchup_faction == 'Demonhunter') {
                            worst_matchup_faction = 'DemonHunter'
                        }
                        var matchup_box_tr = matchup_block[1].querySelectorAll('div.stats-table tr')
                        if (matchup_box_tr.length > 1) {
                            var worst_matchup_win_rate = matchup_box_tr[0].querySelector('td').textContent
                            var worst_matchup_games = matchup_box_tr[1].querySelector('td').textContent
                            archetype['worst_matchup'] = JSON.stringify([worst_matchup_player_class, worst_matchup_win_rate, worst_matchup_games, worst_matchup_faction])
                        }
                    } else {
                        console.log('worst matchup为空')
                    }
                } else {
                    console.log('matchup_box 无内容')
                }
                if (deck_block.length>1) {
                    var deck_boxes = document.querySelectorAll('a.deck-box')
                    var deck_code_reg = /.*\/(.*)\//
                    var pop_deck_href = deck_boxes[0].getAttribute('href')
                    if (pop_deck_href) {
                        var pop_deck_code = deck_code_reg.exec(pop_deck_href)[1]
                        var pop_deck_win_rate = deck_boxes[0].querySelectorAll('div.stats-table tr')[0].querySelector('td').textContent
                        var pop_deck_games = deck_boxes[0].querySelectorAll('div.stats-table tr')[1].querySelector('td').textContent
                        archetype['pop_deck'] = JSON.stringify([pop_deck_code, pop_deck_win_rate, pop_deck_games])
                    } else {
                        console.log('pop deck为空')
                    }
                    var best_deck_href = deck_boxes[1].getAttribute('href')
                    if (best_deck_href) {
                        var best_deck_code = deck_code_reg.exec(best_deck_href)[1]
                        var best_deck_win_rate = deck_boxes[1].querySelectorAll('div.stats-table tr')[0].querySelector('td').textContent
                        var best_deck_games = deck_boxes[1].querySelectorAll('div.stats-table tr')[1].querySelector('td').textContent
                        archetype['best_deck'] = JSON.stringify([best_deck_code, best_deck_win_rate, best_deck_games])
                    } else {
                        console.log('best deck为空')
                    }
                } else {
                    console.log('deck_box 无内容')
                }
                archetype['core_cards'] = []
                archetype['pop_cards'] = []
                var card_list_wrapper = document.querySelectorAll('div.archetype-signature div.card-list-wrapper')
                var core_card_list_items = card_list_wrapper.length>0?card_list_wrapper[0].querySelectorAll('.card-tile'):[]
                var core_cards = []
                for(var item of core_card_list_items) {
                    card_name = item.querySelector('.card-name').textContent
                    card_cost = item.querySelector('.card-cost').textContent
                    card_assert = item.querySelector('img.card-asset').getAttribute('src')
                    card_hsid = card_assert.match(/.*\/(.*)\.[a-zA-Z]*$/)[1]
                    core_cards.push({'name': card_name, 'cost': card_cost, 'card_hsid': card_hsid})
                }
                archetype['core_cards'] = core_cards

                var pop_card_list_items = card_list_wrapper.length>1?card_list_wrapper[1].querySelectorAll('.card-tile'):[]
                var pop_cards = []
                for(var item of pop_card_list_items) {
                    card_name = item.querySelector('.card-name').textContent
                    card_cost = item.querySelector('.card-cost').textContent
                    card_assert = item.querySelector('img.card-asset').getAttribute('src')
                    card_hsid = card_assert.match(/.*\/(.*)\.[a-zA-Z]*$/)[1]
                    pop_cards.push({'name': card_name, 'cost': card_cost, 'card_hsid': card_hsid})
                }
                archetype['pop_cards'] = pop_cards

                var tab_matchup = document.querySelector('#tab-matchups')
                tab_matchup.click()
                setTimeout(function() {
                    var faction_boxes = document.querySelectorAll('div.class-box-container div.box.class-box')
                    var matchup = {'Druid':[], 'Hunter':[], 'Mage':[], 'Paladin':[], 'Priest':[], 'Rogue':[], 'Shaman':[], 'Warlock':[], 'Warrior':[], 'DemonHunter':[]}
                    for (var box of faction_boxes) {
                        var faction = box.querySelector('div.box-title span.player-class').textContent.replace(' ', '')
                        var archetype_list_block = box.querySelectorAll('div.grid-container')[2].querySelectorAll('a.player-class')
                        var archetype_list = []
                        for (var arche of archetype_list_block) {
                            archetype_list.push([arche.textContent])
                        }
                        var data_cells_block = box.querySelectorAll('div.grid-container')[3].querySelectorAll('a.table-cell')
                        data_list = []
                        list_temp = []
                        for(var i=0; i<data_cells_block.length; i++) {
                            list_temp.push(data_cells_block[i].textContent)
                            if (list_temp.length % 3 == 0) {
                                data_list.push(list_temp)
                                list_temp = []
                            }
                        }
                        for (var i=0; i<archetype_list.length; i++) {
                            archetype_list[i].push.apply(archetype_list[i], data_list[i])
                        }
                        matchup[faction] = archetype_list
                    }
                    var matchup_value = []
                    for (var key in matchup) {
                        matchup_value.push(matchup[key])
                    }
                    matchup_value = JSON.stringify(matchup_value)
                    archetype['matchup'] = matchup_value
                    console.log('archetype解析完毕：', archetype)
                    sendMessageToBackground({msg: BG_MSG_ID.MSG_UPDATE_META_BY_CLASS, payload: archetype})
                }, 3000)
            }
            timer_times += 1
            console.log('定时器次数：', timer_times)
        }, 2000)
    } else if (current_mode.payload == MODE_ID.MODE_TIER_LIST) {
        sendMessageToBackground({msg: BG_MSG_ID.TIER_LIST_PAGE_LOADED, payload: null})
    } else if (current_mode.payload == MODE_ID.MODE_META_BY_CLASS_ALL) {
        sendMessageToBackground({msg: BG_MSG_ID.MSG_META_PAGE_LOADED, payload: null})
    } else if (current_mode.payload == MODE_ID.MODE_RANK) {
        // var game_type = {'Standard': 2, 'Wild': 30, 'Arena': 3}
        var game_type = [{name: 'Standard', value: 2}, {name: 'Wild', value: 30}, 
                         {name: 'Arena', value: 3}, {name: 'Duels', value: 55}, {name: 'Classic', value: 58}]
        var json_str = document.querySelector('pre').textContent
        var json_data = JSON.parse(json_str).series.data
        console.log('aaa', json_data)
        var rank_list = []
        for (var faction in json_data) {
            for (var item of json_data[faction]) {
                console.log('bbb', faction, item)
                var type = game_type.filter(v => {
                    if (item.game_type == v.value) {
                        return v.name
                    }
                })
                console.log('cccc', type)
                var format_faction = faction.toUpperCase()=='DEMONHUNTER'?'DemonHunter':firstUpperCase(faction)
                var rank_item = {
                    'faction': format_faction,
                    'game_type': type[0].name,
                    'win_rate': parseFloat(item.win_rate),
                    'date': dateFormat("YYYY-mm-dd HH:MM:SS", new Date())
                }
                rank_list.push(rank_item)
            }
        }
        sendMessageToBackground({msg: BG_MSG_ID.MSG_UPLOAD_RANK_DATA, payload: rank_list})
    } else {
        console.log(dateFormat("YYYY-mm-dd HH:MM:SS", new Date())+':页面未处理')
    }
})



chrome.runtime.onMessage.addListener(function(request, sender, sendResponse)
{
    console.log('content-script收到消息：', request);
    var msg = request.msg
    var payload = request.payload
    switch(msg) {
        case CS_MSG_ID.MSG_ANALYSIS_TRENDING: {
            var objs = document.querySelectorAll('.deck-list>ul>li');
            console.log(objs, objs.length)
            if (objs.length) {
                console.log('load complete!')
                var deck_list = analysis_deck_list_page(msg, objs, 0, objs.length)
                console.log('content-script解析完毕', deck_list)
                // 同时发给background和popup
                sendMessageToBackground({msg: MSG_ID.MSG_ANALYSIS_TRENDING, payload: deck_list})
            } else {
                alert('卡组列表还未加载')
            }
        };
        break;
        case CS_MSG_ID.MSG_ANALYSIS_DECKS_PAGE: {
            var objs = document.querySelectorAll('.deck-list>ul>li')
            if (objs.length) {
                console.log(objs, objs.length)
                var deck_list = analysis_deck_list_page(msg, objs, 1, objs.length)
                sendMessageToBackground({msg: MSG_ID.MSG_ANALYSIS_DECKS, payload: deck_list})
            } else {
                alert('卡组列表还未加载')
            }
        };
        break;
        case CS_MSG_ID.MSG_NEW_DECKS_PAGE: {
            var timer_times = 0
            var timer = window.setInterval(function() {
                var deck_list_block = document.querySelectorAll('.deck-list>ul>li')
                timer_times += 1
                console.log('第'+timer_times+'次查看卡组页是否加载完毕')
                if (deck_list_block.length) {
                    console.log('页面加载完成')
                    clearInterval(timer)
                    console.log(deck_list_block, deck_list_block.length)
                    var deck_list = analysis_deck_list_page(msg, deck_list_block, 1, deck_list_block.length)
                    sendMessageToBackground({msg: MSG_ID.MSG_ANALYSIS_DECKS, payload: deck_list})
                }
            }, 2000)
        };
        break;
        case CS_MSG_ID.MSG_ANALYSIS_META_BY_CLASS1: {
            var objs = document.querySelectorAll('div.class-box-container div.box.class-box')
            var filter_faction = payload.faction
            var rank_range = payload.rank_range[0]
            var list_array = {}
            for(var item of objs) {
                var faction = item.querySelector('div.box-title span.player-class').textContent
                faction = firstUpperCase(faction.replace(' ', ''))
                if (faction == 'Demonhunter') {
                    faction = 'DemonHunter'
                }
                console.log(filter_faction, filter_faction.length, faction, filter_faction.indexOf(faction))
                if (filter_faction.length>0 && filter_faction.indexOf(faction)<0) {
                    continue
                }
                list_array[faction] = {}
                var archetype_list_block = item.querySelectorAll('div.grid-container')[2].querySelectorAll('a.player-class')
                var archetype_list = []
                for(var arche of archetype_list_block) {
                    archetype_list.push({faction: faction, archetype: arche.textContent, href: arche.getAttribute('href')})
                }
                var archetype_list_other_block = item.querySelectorAll('div.grid-container')[2].querySelector('span.player-class div.tooltip-wrapper h4')
                if (archetype_list_other_block) {
                    archetype_list.push({faction: faction, archetype: archetype_list_other_block.textContent, href:''})
                }
                var data_cells = item.querySelectorAll('div.grid-container')[3].querySelectorAll('.table-cell')
                var data_list = []
                var temp_list = []
                for(var i=0; i<data_cells.length; i++) {
                    temp_list.push(data_cells[i].textContent)
                    if (temp_list.length % 3 == 0) {
                        data_list.push(temp_list)
                        temp_list = []
                    }
                }
                for (var i=0; i<archetype_list.length; i++) {
                    var item = archetype_list[i]
                    item['winrate'] = parseFloat(data_list[i][0].replace('%', ''))
                    item['popularity'] = parseFloat(data_list[i][1].replace('%', ''))
                    item['games'] = parseInt(data_list[i][2].replace(',', ''))
                    item['rank_range'] = rank_range
                    item['checked'] = false
                    item['create_time'] = dateFormat("YYYY-mm-dd HH:MM:SS", new Date())
                }
                list_array[faction] = archetype_list
            }
            console.log('meta数据抓取完毕', list_array)
            sendMessageToBackground({msg: MSG_ID.MSG_ANALYSIS_META_BY_CLASS, payload: {rank_range: rank_range, list: list_array}})
        };
        break;
        case CS_MSG_ID.MSG_ANALYSIS_META_BY_CLASS: {
            var rank_range = payload.range
            var filter_faction = payload.faction
            var rank_range_buttons = get_rank_range_button()
            console.log('aa', rank_range, rank_range_buttons)
            var current_range_block = rank_range_buttons.filter(item => {
                if (item.range == rank_range) {
                    return item.block
                }
            })[0].block
            console.log(current_range_block, filter_faction)
            current_range_block.click()
            var timer_times = 0
            var timer = window.setInterval(function() {
                var objs = document.querySelectorAll('div.class-box-container div.box.class-box')
                timer_times += 1
                console.log('第'+timer_times+'次查看页面是否加载完毕')
                if (objs.length) {
                    clearInterval(timer)
                    var list_array = {}
                    for(var item of objs) {
                        var faction = item.querySelector('div.box-title span.player-class').textContent
                        faction = firstUpperCase(faction.replace(' ', ''))
                        if (faction == 'Demonhunter') {
                            faction = 'DemonHunter'
                        }
                        console.log(filter_faction, filter_faction.length, faction, filter_faction.indexOf(faction))
                        if (filter_faction.length>0 && filter_faction.indexOf(faction)<0) {
                            continue
                        }
                        list_array[faction] = {}
                        var archetype_list_block = item.querySelectorAll('div.grid-container')[2].querySelectorAll('a.player-class')
                        var archetype_list = []
                        for(var arche of archetype_list_block) {
                            archetype_list.push({faction: faction, archetype: arche.textContent, href: arche.getAttribute('href')})
                        }
                        var archetype_list_other_block = item.querySelectorAll('div.grid-container')[2].querySelector('span.player-class div.tooltip-wrapper h4')
                        if (archetype_list_other_block) {
                            archetype_list.push({faction: faction, archetype: archetype_list_other_block.textContent, href:''})
                        }
                        var data_cells = item.querySelectorAll('div.grid-container')[3].querySelectorAll('.table-cell')
                        var data_list = []
                        var temp_list = []
                        for(var i=0; i<data_cells.length; i++) {
                            temp_list.push(data_cells[i].textContent)
                            if (temp_list.length % 3 == 0) {
                                data_list.push(temp_list)
                                temp_list = []
                            }
                        }
                        for (var i=0; i<archetype_list.length; i++) {
                            var item = archetype_list[i]
                            item['winrate'] = parseFloat(data_list[i][0].replace('%', ''))
                            item['popularity'] = parseFloat(data_list[i][1].replace('%', ''))
                            item['games'] = parseInt(data_list[i][2].replace(',', ''))
                            item['rank_range'] = rank_range
                            item['checked'] = false
                            item['create_time'] = dateFormat("YYYY-mm-dd HH:MM:SS", new Date())
                        }
                        list_array[faction] = archetype_list
                    }
                    console.log('meta数据抓取完毕', list_array, rank_range)
                    sendMessageToBackground({msg: MSG_ID.MSG_ANALYSIS_META_BY_CLASS, payload: {rank_range: rank_range, list: list_array}})
                }
            }, 2000)
        };
        break;
        case CS_MSG_ID.MSG_UPDATE_TIER_LIST: {
            console.log('准备解析TierList', msg, payload)
            var rank_range = payload.range
            var rank_range_buttons = get_rank_range_button()
            var current_range_block = rank_range_buttons.filter(item => {
                console.log(item, item.range, rank_range)
                if (item.range == rank_range) {
                    return item.block
                }
            })[0].block
            console.log(current_range_block)
            current_range_block.click()
            var timer_times = 0
            var timer = window.setInterval(function() {
                var tier_list_block = document.querySelectorAll('div.archetype-tier-list div.tier')
                timer_times += 1
                console.log('第'+timer_times+'次查看页面是否加载完毕')
                if (tier_list_block.length) {
                    console.log('页面加载完成')
                    clearInterval(timer)
                    console.log(tier_list_block, tier_list_block.length)
                    var tier_list = []
                    for (var item of tier_list_block) {
                        var tier = item.querySelector('div.tier-header').innerText.split('\n')[0]
                        var archetype_list_items = item.querySelectorAll('li.archetype-list-item')
                        for (var arche of archetype_list_items) {
                            var archetype_name = arche.querySelector('div.archetype-name').textContent
                            var faction = archetype_name.split(' ')
                            if (faction.length>2 && faction[faction.length-2].toLowerCase()=='demon') {
                                faction = 'DemonHunter'
                            } else {
                                faction = faction[faction.length-1]
                                if (faction == 'Handlock') {
                                    faction = 'Warlock'
                                }
                            }
                            var win_rate = parseFloat(arche.querySelector('div.archetype-data').textContent)
                            var arche_obj = {
                                'tier': tier,
                                'archetype_name': archetype_name,
                                'faction': faction,
                                'win_rate': win_rate,
                                'rank_range': rank_range,
                                'update_time': dateFormat("YYYY-mm-dd HH:MM:SS", new Date())
                            }
                            tier_list.push(arche_obj)
                        }
                    }
                    console.log('aaaaa', tier_list)
                    sendMessageToBackground({msg: BG_MSG_ID.MSG_ANALYSIS_TIER_END, payload: {range: rank_range, list: tier_list}})
                }
            }, 2000)
        };
        break;
        default: {
            if (sendResponse) {
                console.log('未知消息')
                sendResponse('未知消息')
            }
        }
    }
});

function sendMessageToBackground(message) {
	chrome.runtime.sendMessage(message, function(response) {
		console.log('收到background或者popup回复：', response);
	});
}

function asyncSendMessageToBackground(message) {
    return new Promise(resolve => {
        chrome.runtime.sendMessage(message, function(response) {
            console.log('收到background或者popup回复：', response);
            resolve(response)
        });
    })
}

function analysis_deck_list_page(msg, objs, start, end) {
    var deck_list = []
    console.log('analysis_deck_list_page', start, end)
    for (var i=start; i<end; i++) {
        var item = objs[i]
        var deck_item = item.querySelector('a')
        var href = deck_item.getAttribute('href')
        var deck_id = href.match(/\/.*\/(.*)\//)[1]
        var faction = deck_item.getAttribute('data-card-class')
        if(faction === 'DEMONHUNTER') {
            faction = 'DemonHunter'
        } else {
            faction = firstUpperCase(faction)
        }
        var deck_name = item.querySelector('.row h3.deck-name').textContent
        var dust_cost = parseInt(item.querySelector('.row .dust-cost').textContent)
        var win_rate = item.querySelector('.row .win-rate').textContent
        win_rate = parseFloat(win_rate.replace('%', ''))
        var duration = item.querySelector('.row .duration').textContent
        duration = parseFloat(duration.trim().split(' ')[0])
        var game_count = item.querySelector('.row .game-count').textContent
        game_count = parseInt(game_count.replace(',', ''))
        var url
        var reg_str = /.*\/#.*/ //是否有#号存在
        if (reg_str.test(href)) {
            url = 'https://hsreplay.net'+href+'&tab=overview'
        } else {
            url = 'https://hsreplay.net'+href+'#tab=overview'
        }
        // trending卡组调整为钻石-传说分段
        if (msg == CS_MSG_ID.MSG_ANALYSIS_TRENDING) {
            url = 'https://hsreplay.net'+href+'#rankRange=DIAMOND_THROUGH_LEGEND&tab=overview'
        }
        deck_list.push({
            deck_id: deck_id,
            faction: faction,
            url: url,
            deck_name: deck_name,
            dust_cost: dust_cost,
            win_rate: win_rate,
            duration: duration,
            game_count: game_count,
            handled_flag: false
        })
    }
    console.log('deck_list解析完毕', deck_list)
    return deck_list
}

function analysis_tier_list_page(all_range_objs, current_range_obj, list_array, count) {
    var timer_times = 0
    var timer = window.setInterval(function() {
        var tier_list_block = document.querySelectorAll('div.archetype-tier-list div.tier')
        timer_times += 1
        console.log('第'+timer_times+'次查看页面是否加载完毕')
        if (tier_list_block.length) {
            console.log('页面加载完成')
            clearInterval(timer)
            console.log(tier_list_block, tier_list_block.length)
            var tier_list = []
            for (var item of tier_list_block) {
                var tier = item.querySelector('div.tier-header').innerText.split('\n')[0]
                var archetype_list_items = item.querySelectorAll('li.archetype-list-item')
                for (var arche of archetype_list_items) {
                    var archetype_name = arche.querySelector('div.archetype-name').textContent
                    var faction = archetype_name.split(' ')
                    if (faction.length>2 && faction[faction.length-2].toLowerCase()=='demon') {
                        faction = 'DemonHunter'
                    } else {
                        faction = faction[faction.length-1]
                        if (faction == 'Handlock') {
                            faction = 'Warlock'
                        }
                    }
                    var win_rate = parseFloat(arche.querySelector('div.archetype-data').textContent)
                    var arche_obj = {
                        'tier': tier,
                        'archetype_name': archetype_name,
                        'faction': faction,
                        'win_rate': win_rate,
                        'rank_range': current_range_obj.range,
                        'update_time': dateFormat("YYYY-mm-dd HH:MM:SS", new Date())
                    }
                    tier_list.push(arche_obj)
                }
            }
            list_array.push({range: current_range_obj.range, list: tier_list})
            count += 1
            console.log('当前tierlist页面解析完毕：', list_array, current_range_obj)
            console.log('current_range_obj.range='+current_range_obj.range+', all_range_objs[all_range_objs.length-1]='+all_range_objs[all_range_objs.length-1].range)
            if (current_range_obj.range != all_range_objs[all_range_objs.length-1].range) {
                for (var i=0; i<all_range_objs.length; i++) {
                    if (all_range_objs[i].range == current_range_obj.range) {
                        current_range_obj = all_range_objs[i+1]
                        current_range_obj.block.click()
                    }
                    console.log('新的current_range_obj.range=', current_range_obj)
                    if (count < 2) {
                        analysis_tier_list_page(all_range_objs, current_range_obj, list_array) 
                    }
                }
            }
        }
    }, 2000)
}

function get_rank_range_button() {
    var rank_range_objs = []
    var selectable_item = document.querySelectorAll('#rank-range-filter li.selectable')
    for(var item of selectable_item) {
        if (item.innerText == 'Legend: Top 1,000') { rank_range_objs.push({block: item, range: 'TOP_1000_LEGEND'}) }
        else if (item.innerText == 'Legend') { rank_range_objs.push({block: item, range: 'LEGEND'}) }
        else if (item.innerText == 'Diamond: 4–1') { rank_range_objs.push({block: item, range: 'DIAMOND_FOUR_THROUGH_DIAMOND_ONE'}) }
        else if (item.innerText == 'Diamond through Legend') { rank_range_objs.push({block: item, range: 'DIAMOND_THROUGH_LEGEND'}) }
        else if (item.innerText == 'Bronze through Gold') { rank_range_objs.push({block: item, range: 'BRONZE_THROUGH_GOLD'}) }
    }
    return rank_range_objs
}