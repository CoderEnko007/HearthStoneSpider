var time_frame = ''
var time_range_array = ['', 'LAST_7_DAYS', 'LAST_30_DAYS', 'CURRENT_EXPANSION', 'CURRENT_PATCH']
// if (localStorage['time_frame']=='LAST_7_DAYS') {
//     $('input[name="time_frame"]').attr('checked', 'true')
//     time_frame = 'LAST_7_DAYS'
// }
for (let i in time_range_array) {
    if (localStorage['time_frame'] == time_range_array[i]) {
        let objs = $('input[name="time_range"]')
        objs[i].setAttribute('checked', true)
    }
}

$('#open_trending').click(() => {
    console.log('打开趋势页面')
    getCurrentTabId(tabId => {
        chrome.tabs.update(tabId, {url: 'https://hsreplay.net/trending'})
    })
})

$('#analysis_trending_page').click(() => {
    sendMessageToContentScript({msg: CS_MSG_ID.MSG_ANALYSIS_TRENDING, payload: null})
})

var deck_start_page=0
var deck_end_page=1
var current_page=0
var rank_mode = 'Standard'
var deck_rank_range = 'DIAMOND_THROUGH_LEGEND'
// var decks_page_base_url = 'https://hsreplay.net/decks/#rankRange=DIAMOND_THROUGH_LEGEND&timeRange=LAST_7_DAYS'
var default_decks_url = 'https://hsreplay.net/decks/'
// var decks_page_base_url = 'https://hsreplay.net/decks/#rankRange=DIAMOND_THROUGH_LEGEND&includedCards=61503'
$('#open_deck').click(() => {
    console.log('打开卡组页面')

    var objs1 = $("input[name='deck_rank_range']")
    for (let i in objs1) {
        if (objs1[i].checked) {
            deck_rank_range = objs1[i].value
        }
    }
    decks_page_base_url = default_decks_url + '#rankRange=' + deck_rank_range

    if (localStorage['time_frame']=='LAST_7_DAYS') {
        decks_page_base_url = decks_page_base_url + '&timeRange=LAST_7_DAYS'
    } else if (localStorage['time_frame']=='CURRENT_EXPANSION') {
        decks_page_base_url = decks_page_base_url + '&timeRange=CURRENT_EXPANSION'
    } else if (localStorage['time_frame']=='LAST_30_DAYS') {
        decks_page_base_url = decks_page_base_url + '&timeRange=LAST_30_DAYS'
    } else if (localStorage['time_frame']=='CURRENT_PATCH') {
        decks_page_base_url = decks_page_base_url + '&timeRange=CURRENT_PATCH'
    }

    var objs2 = $("input[name='deck-mode']")
    if (objs2[1].checked) {
        rank_mode = 'Wild'
        decks_page_base_url = decks_page_base_url+'&gameType=RANKED_WILD&wildCard=yes'
    } else if (objs2[2].checked) {
        rank_mode = 'Classic'
        decks_page_base_url = decks_page_base_url+'&gameType=RANKED_CLASSIC'
    } else {
        rank_mode = 'Standard'
    }

    deck_start_page = $('#start_page').val()
    deck_end_page = $('#end_page').val()

    var url = decks_page_base_url
    if (deck_start_page > 1) {
        url = decks_page_base_url+'&page='+deck_start_page
    }
    
    getCurrentTabId(tabId => {
        chrome.tabs.update(tabId, {url: url})
    })
})

$('#analysis_deck_page').click(() => {
    var objs1 = $("input[name='deck_rank_range']")
    for (let i in objs1) {
        if (objs1[i].checked) {
            deck_rank_range = objs1[i].value
        }
    }
    decks_page_base_url = default_decks_url + '#rankRange=' + deck_rank_range

 
    if (localStorage['time_frame']=='LAST_7_DAYS') {
        decks_page_base_url = decks_page_base_url + '&timeRange=LAST_7_DAYS'
    } else if (localStorage['time_frame']=='CURRENT_EXPANSION') {
        decks_page_base_url = decks_page_base_url + '&timeRange=CURRENT_EXPANSION'
    } else if (localStorage['time_frame']=='LAST_30_DAYS') {
        decks_page_base_url = decks_page_base_url + '&timeRange=LAST_30_DAYS'
    } else if (localStorage['time_frame']=='CURRENT_PATCH') {
        decks_page_base_url = decks_page_base_url + '&timeRange=CURRENT_PATCH'
    }

    var objs2 = $("input[name='deck-mode']")
    if (objs2[1].checked) {
        rank_mode = 'Wild'
        decks_page_base_url = decks_page_base_url+'&gameType=RANKED_WILD&wildCard=yes'
    } else if (objs2[2].checked) {
        rank_mode = 'Classic'
        decks_page_base_url = decks_page_base_url+'&gameType=RANKED_CLASSIC'
    } else {
        rank_mode = 'Standard'
    }

    deck_start_page = $('#start_page').val()?$('#start_page').val():deck_start_page
    deck_end_page = $('#end_page').val()?$('#end_page').val():deck_end_page
    current_page = parseInt(deck_start_page)
    console.log(deck_start_page, deck_end_page)
    $('#deck_info').text('开始解析Deck页面（'+deck_start_page+'页-'+deck_end_page+'页）,当前第1页')
    sendMessageToContentScript({msg: CS_MSG_ID.MSG_ANALYSIS_DECKS_PAGE, payload: {start_page: deck_start_page, end_page: deck_end_page}})
})

// var time_frame = 'LAST_7_DAYS'
// var time_frame = ''
// var time_frame = $('input[name="time_frame"]').is(":checked")?'LAST_7_DAYS':''
var rank_range = 'BRONZE_THROUGH_GOLD'
var faction_array = []
var rank_range_array = []
$('#open_winrate').click(() => {
    console.log('打开meta页面')
    time_frame = localStorage['time_frame']
    rank_range_array = []
    $('input[name="rank_range"]:checked').each((i, item) => {
        rank_range_array.push(item.value)
    })
    console.log('rank_range_array:', rank_range_array)
    getCurrentTabId(tabId => {
        var base_url = 'https://hsreplay.net/meta/'
        var hash = ''
        if (time_frame && time_frame !== 'NONE') {
            hash +='#timeFrame='+time_frame
        }
        if (rank_range_array.length) {
            hash = hash?hash+'&rankRange='+rank_range_array[0]:'#rankRange='+rank_range_array[0]
        }
        var url = hash?base_url+hash+'&tab=archetypes':base_url+'#tab=archetypes'
        console.log('url:', url)
        chrome.tabs.update(tabId, {url: url})
    })
})

$('#analysis_winrate_page').click(() => {
    console.log('开始解析meta页面')
    time_frame = localStorage['time_frame']
    rank_range_array = []
    $('input[name="rank_range"]:checked').each((i, item) => {
        rank_range_array.push(item.value)
    })
    faction_array = []
    $('input[name="faction"]:checked').each((i, item) => {
        faction_array.push(item.value)
    })
    console.log(rank_range_array, faction_array)
    sendMessageToContentScript({msg: CS_MSG_ID.MSG_ANALYSIS_META_BY_CLASS, 
        payload: {time_frame:time_frame, rank_range: rank_range_array, faction: faction_array}})
})

$('#analysis_winrate_page_all').click(() => {
    time_frame = localStorage['time_frame']
    rank_range_array = []
    $('input[name="rank_range"]:checked').each((i, item) => {
        rank_range_array.push({checked: false, range: item.value})
    })
    faction_array = []
    $('input[name="faction"]:checked').each((i, item) => {
        faction_array.push(item.value)
    })
    var base_url = 'https://hsreplay.net/meta/'
    var hash = ''
    if (time_frame) {
        hash +='#timeFrame='+time_frame
    }
    if (rank_range_array.length) {
        hash = hash?hash+'&rankRange='+rank_range_array[0].range:'#rankRange='+rank_range_array[0].range
    }
    var url = hash?base_url+hash+'&tab=archetypes':base_url+'#tab=archetypes'
    console.log('准备打开url:', url)
    $('#meta_info').text('准备打开meta页面：'+rank_range_objs[rank_range_array[0].range])
    sendMessageToBackground({
        msg: BG_MSG_ID.MSG_UPDATE_META_BY_CLASS_ALL,
        payload: {rank_range: rank_range_array, faction: faction_array}}, 
        function(response) {
            console.log('来自后台：', response)
            var msg = response.msg
            var payload = response.payload
            if (msg == BG_MSG_ID.MSG_UPDATE_META_BY_CLASS_ALL) {
                chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
                    console.log(tabs[0]);
                    if (tabs[0].url == url) {
                        sendMessageToBackground({msg: BG_MSG_ID.MSG_META_PAGE_LOADED, payload: null})
                    } else {
                        getCurrentTabId(tabId => {
                            console.log('打开Meta页面:', payload)
                            chrome.tabs.update(tabId, {url: url})
                        })
                    }
                });
            }
    })
})

$('#meta-select-all').click(() => {
    // 全选
    console.log('全选')
    $('input[name="faction"]').each((i, item) => {
        item.checked = true
    })
    faction_array = []
    $('input[name="faction"]:checked').each((i, item) => {
        faction_array.push(item.value)
    })
})
$('#meta-unselect-all').click(() => {
    // 全不选
    console.log('全不选')
    $('input[name="faction"]').each((i, item) => {
        item.checked = false
    })
    faction_array = []
})

var tier_list_rank_range_array = []
$('#analysis_tier_list_page').click(() => {
    console.log('打开Tier list页面')
    time_frame = localStorage['time_frame']
    tier_list_rank_range_array = []
    $('input[name="tier_rank_range"]:checked').each((i, item) => {
        tier_list_rank_range_array.push({checked: false, range: item.value})
    })
    var base_url = 'https://hsreplay.net/meta/'
    var hash = ''
    var url = ''
    // var tier_list_url = []
    if (time_frame) {
        hash +='#timeFrame='+time_frame
    }
    if (tier_list_rank_range_array.length) {
        var item = tier_list_rank_range_array[0].range
        hash = hash?hash+'&rankRange='+item:'#rankRange='+item
        url = hash?base_url+hash:base_url
        console.log('url:', url)
    }
    console.log('tier_list_rank_range_array:', tier_list_rank_range_array)
    $('#tier_info').text('准备打开TierList页面：'+rank_range_objs[tier_list_rank_range_array[0].range])
    sendMessageToBackground({msg: BG_MSG_ID.MSG_UPDATE_TIER_LIST, payload:tier_list_rank_range_array}, function(response) {
        console.log('来自后台：', response)
        var msg = response.msg
        var payload = response.payload
        if (msg == BG_MSG_ID.MSG_UPDATE_TIER_LIST) {
            getCurrentTabId(tabId => {
                console.log('打开Tier List页面:', payload)
                chrome.tabs.update(tabId, {url: url})
            })
        }
    })
})

$('#open_tier_list').click(() => {
    var base_url = 'https://hsreplay.net/meta/'
    var hash = ''
    var url = ''
    tier_list_rank_range_array = []
    time_frame = localStorage['time_frame']
    $('input[name="tier_rank_range"]:checked').each((i, item) => {
        tier_list_rank_range_array.push(item.value)
    })
    if (time_frame) {
        hash +='#timeFrame='+time_frame
    }
    if (tier_list_rank_range_array.length) {
        hash = hash?hash+'&rankRange='+tier_list_rank_range_array[0]:'#rankRange='+tier_list_rank_range_array[0]
        url = hash?base_url+hash:base_url
        console.log('url:', url)
        getCurrentTabId(tabId => {
            console.log('打开TierList页面')
            chrome.tabs.update(tabId, {url: url})
        })
    }
})

$('#open_rank_page').click(() => {
    var url = 'https://hsreplay.net/analytics/query/player_class_performance_summary/'
    getCurrentTabId(tabId => {
        console.log('打开Rank页面')
        chrome.tabs.update(tabId, {url: url})
    })
})

$('#analysis_rank_page').click(() => {
    var url = 'https://hsreplay.net/analytics/query/player_class_performance_summary/'
    $('#rank_info').text('打开Rank页面，准备解析')
    getCurrentTabId(tabId => {
        console.log('打开Rank页面')
        chrome.tabs.update(tabId, {url: url}, function() {
            sendMessageToBackground({msg: BG_MSG_ID.MSG_UPDATE_RANK_DATA, payload: null})
        })
    })
})

$('#trending_webhook').click(async () => {
    var webhook = 'https://cloud.minapp.com/oserve/v1/incoming-webhook/eOddYi3a2H/'
    fetch(webhook).then(res => res.json())
                .then(data => console.log(data))
})

$('#rank_webhook').click(async () => {
    var webhook = 'https://cloud.minapp.com/oserve/v1/incoming-webhook/ndhvGONeNt'
    fetch(webhook).then(res => res.json())
                .then(data => console.log(data))
})

$('#rank_webhook1').click(async () => {
    var webhook = 'https://cloud.minapp.com/oserve/v1/incoming-webhook/T1vA85AhPG'
    fetch(webhook).then(res => res.json())
                .then(data => console.log(data))
})

$('#rank_range_webhook').click(async () => {
    var webhook = 'https://cloud.minapp.com/oserve/v1/incoming-webhook/elzp6Ttp2L'
    fetch(webhook).then(res => res.json())
                .then(data => console.log(data))
    var webhook1 = 'https://cloud.minapp.com/oserve/v1/incoming-webhook/ey491UwqmO'
    fetch(webhook1).then(res => res.json())
                .then(data => console.log(data))
})

$('#archetype_detail_webhook').click(async () => {
    var webhook = 'https://cloud.minapp.com/oserve/v1/incoming-webhook/ey491UwqmO'
    fetch(webhook).then(res => res.json())
                .then(data => console.log(data))
})

$('#tier_list_webhook').click(async () => {
    var webhook = 'https://cloud.minapp.com/oserve/v1/incoming-webhook/RGFLY7CmCp'
    fetch(webhook).then(res => res.json())
                .then(data => console.log(data))
})

function getBestDeck(url) {
    return new Promise(async (resolve) => {
        var res = await fetch(url)
        var jsonData = await res.json()
        var next_url = jsonData['next']
        console.log('next_url:', next_url)
        var results = jsonData['results']
        var deck_list = []
        for (var item of results) {
            if (item['archetype'] != 'Other') {
                var best_deck = JSON.parse(item['best_deck'])
                if (best_deck.length<=0) {
                    continue
                }
                var deck_id = best_deck[0]
                var deck_uri = 'https://hsreplay.net/decks/'+deck_id+'/#rankRange=DIAMOND_THROUGH_LEGEND&tab=overview'
                deck_list.push({
                    'deck_id': deck_id,
                    'faction': item['faction']['id'],
                    'url': deck_uri,
                    'deck_name': item['archetype'],
                    'win_rate': parseFloat(best_deck[1].replace('%', '')),
                    'game_count': parseInt(best_deck[2]),
                    'handled_flag': false
                })
                console.log(item['faction']['id'], item['archetype'], deck_uri)
            }
        }
        resolve({next_url: next_url, deck_list: deck_list})
    })
}

var best_deck_num = 0
var current_num = 1
$('#update_bestdeck').click(async () => {
    var bg = chrome.extension.getBackgroundPage();
    var url = 'http://47.98.187.217/winrate/?rank_range=BRONZE_THROUGH_GOLD&format=json&create_time='+dateFormat("YYYY-mm-dd", new Date())
    var deck_list = []
    $('#best_deck_info').text('开始获取需要更新的卡组(请耐心等待)...')
    var result = await getBestDeck(url)
    deck_list.push.apply(deck_list, result.deck_list)
    while (result.next_url) {
        result = await getBestDeck(result.next_url)
        deck_list.push.apply(deck_list, result.deck_list)
    }
    best_deck_num = deck_list.length
    $('#best_deck_info').text('需要处理的卡组共'+best_deck_num+'个, 开始处理..')
    // bg.temp_deck_list = deck_list
    sendMessageToBackground({msg: BG_MSG_ID.MSG_ANALYSIS_BEST_DECKS, payload:deck_list}, function(response) {
        console.log('来自后台：', response)
        var msg = response.msg
        var payload = response.payload
        if (msg == BG_MSG_ID.MSG_ANALYSIS_BEST_DECKS) {
            $('#best_deck_info').text('正在解析：'+current_num+'/'+best_deck_num+', '+payload[0].deck_name)
            getCurrentTabId(tabId => {
                console.log('打开BestDeck卡组:', tabId, payload[0])
                chrome.tabs.update(tabId, {url: payload[0].url})
            })
        }
    })
})

// 监听来自content-script的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse)
{
	console.log('popup收到来自content-script的消息：', request);
	// console.log(request, sender, sendResponse);
    // sendResponse('我是popup，我已收到你的消息：' + request.msg);
    var bg = chrome.extension.getBackgroundPage();
    time_frame = localStorage['time_frame']
    switch(request.msg) {
        case MSG_ID.MSG_ANALYSIS_DECKS:
        case MSG_ID.MSG_ANALYSIS_TRENDING: {
            var deck_list = bg.getTempDeckList();
            var current_mode = bg.current_mode
            console.log('popup listerner:', deck_list, current_mode)
            if (deck_list.length) {
                // 测试单个卡组
                // var i=0
                // if (!deck_list[i].handled_flag) {
                //     getCurrentTabId(tabId => {
                //         console.log('打开卡组页:', tabId, deck_list[i])
                //         chrome.tabs.update(tabId, {url: deck_list[i].url})
                //     })
                // } else {
                //     if (request.msg == MSG_ID.MSG_ANALYSIS_DECKS) {
                //         current_page += 1
                //     }
                //     if (request.msg == MSG_ID.MSG_ANALYSIS_TRENDING || current_page > deck_end_page) {
                //         alert('卡组页面解析完毕！')
                //     } else {
                //         var url = base_url+'&page='+current_page
                //         console.log('打开下一页卡组页：', url)
                //         getCurrentTabId(tabId => {
                //             chrome.tabs.update(tabId, {url: url}, function(tab) {
                //                 console.log('testtest11111 tab_id:', tabId, tab)
                //                 // sendMessageToContentScript({msg: CS_MSG_ID.MSG_NEW_DECKS_PAGE, payload: null})
                //                 setTimeout(function() {
                //                     console.log(dateFormat("YYYY-mm-dd HH:MM:SS", new Date())+':popup发送消息，打开新页面')
                //                     chrome.tabs.sendMessage(tab.id, {msg: CS_MSG_ID.MSG_NEW_DECKS_PAGE, payload: null});
                //                 }, 2000)
                //             })
                //         })
                //     }
                // }
                for (var i=0; i<deck_list.length; i++) {
                    if (!deck_list[i].handled_flag) {
                        if (current_mode == MODE_ID.MODE_BEST_DECKS) {
                            current_num += 1
                            $('#best_deck_info').text('正在解析：'+current_num+'/'+best_deck_num+', '+deck_list[i].deck_name)
                        } else if (current_mode == MODE_ID.MODE_DECKS) {
                            var text = $('#deck_info').text().split(' ')[0]
                            $('#deck_info').text(text+' 开始解析('+(i+1)+'/'+deck_list.length+')-'+deck_list[i].deck_name)
                        }
                        getCurrentTabId(tabId => {
                            console.log('打开卡组页:', i, deck_list[i])
                            chrome.tabs.update(tabId, {url: deck_list[i].url})
                        })
                        return
                    }
                }
                console.log('current_mode:', current_mode)
                // if (current_mode == MODE_ID.MODE_DECKS) {
                //     break
                // }
                if (request.msg == MSG_ID.MSG_ANALYSIS_DECKS) {
                    current_page += 1
                }
                if (request.msg == MSG_ID.MSG_ANALYSIS_TRENDING || current_page > deck_end_page || current_mode == MODE_ID.MODE_BEST_DECKS) {
                    alert('卡组页面解析完毕！')
                    current_num = 0
                    if (current_mode == MODE_ID.MODE_BEST_DECKS) {
                        $('#best_deck_info').text('处理完毕')
                    } else if (current_mode == MODE_ID.MODE_DECKS) {
                        $('#deck_info').text('处理完毕')
                    }
                    sendMessageToBackground({msg: MSG_ID.MSG_SET_CURRENT_MODE, payload: MODE_ID.MODE_NONE})
                } else {
                    var url = decks_page_base_url+'&page='+current_page
                    console.log('打开下一页卡组页：', url)
                    $('#deck_info').text('开始解析第'+current_page+'页')
                    getCurrentTabId(tabId => {
                        chrome.tabs.update(tabId, {url: url}, function(tab) {
                            // sendMessageToContentScript({msg: CS_MSG_ID.MSG_NEW_DECKS_PAGE, payload: null})
                            setTimeout(function() {
                                console.log(dateFormat("YYYY-mm-dd HH:MM:SS", new Date())+':popup发送消息，打开新页面')
                                chrome.tabs.sendMessage(tab.id, {msg: CS_MSG_ID.MSG_NEW_DECKS_PAGE, payload: null});
                            }, 5000)
                        })
                    })
                }
            }
        };
        break;
        case POP_MSG_ID.MSG_OPEN_MULLIGAN_PAGE: {
            var mode = 'RANKED_STANDARD'
            if (rank_mode == 'Wild') {
                mode = 'RANKED_WILD'
            } else if (rank_mode == 'Classic') {
                mode = 'RANKED_CLASSIC'
            }
            var time_range_str = localStorage['time_frame'] == 'CURRENT_PATCH'?'&TimeRange='+localStorage['time_frame']:''
            time_range_str = localStorage['time_frame'] == 'CURRENT_EXPANSION'?'&TimeRange='+localStorage['time_frame']:time_range_str
            var url = 'https://hsreplay.net/analytics/query/single_deck_mulligan_guide_v2/?GameType='+mode+'&LeagueRankRange='+deck_rank_range+'&Region=ALL&PlayerInitiative=ALL&deck_id='+request.payload.deck_id+time_range_str
            console.log('准备打开mulligan页面', url)
            getCurrentTabId(tabId => {
                console.log('打开mulligan页:', tabId, request)
                chrome.tabs.update(tabId, {url: url})
            })
        };
        break;
        case MSG_ID.MSG_ANALYSIS_META_BY_CLASS: {
            var rank_range = request.payload.rank_range
            var meta_info = bg.meta_info
            console.log('rank_range:', rank_range, request.payload)
            if (rank_range == 'BRONZE_THROUGH_GOLD') {
                // 是青铜-黄金则跳转并抓取详细数据
                var list_array = meta_info.list
                for (var faction in list_array) {
                    var faction_list = list_array[faction]
                    for (var i=0; i<faction_list.length; i++) {
                        var item = faction_list[i]
                        if (!item.checked && item.href!='') {
                            var url = 'https://hsreplay.net'+item.href+'#rankRange=DIAMOND_THROUGH_LEGEND'
                            // var url = 'https://hsreplay.net'+item.href+'#rankRange=BRONZE_THROUGH_GOLD'
                            console.log('准备打开archetype页面aa', url)
                            var archetype_name = item.href.split('/')
                            archetype_name = archetype_name[archetype_name.length-1]
                            $('#meta_info').text('解析卡组模板（青铜-黄金）：'+(i+1)+'/'+faction_list.length+' '+archetype_name)
                            getCurrentTabId(tabId => {
                                console.log('打开archetype页:', tabId, request)
                                chrome.tabs.update(tabId, {url: url})
                            })
                            return
                        }
                    }
                }
                console.log('list_array:', list_array)
                var meta_range_array = bg.meta_list_rank_range_array
                if (list_array && meta_range_array.length>1) {
                    console.log('BRONZE_THROUGH_GOLD解析完毕！')
                    $('#meta_info').text('青铜-黄金分段解析完毕，正在打开'+rank_range_objs[meta_range_array[1].range]+'页面')
                    // sendMessageToBackground({msg: MSG_ID.MSG_SET_CURRENT_MODE, payload: MODE_ID.MODE_NONE})
                    var base_url = 'https://hsreplay.net/meta/'
                    var hash = ''
                    if (time_frame) {
                        hash +='#timeFrame='+time_frame
                    }
                    if (meta_range_array.length) {
                        hash = hash?hash+'&rankRange='+meta_range_array[1].range:'#rankRange='+meta_range_array[1].range
                    }
                    var url = hash?base_url+hash+'&tab=archetypes':base_url+'#tab=archetypes'
                    console.log('准备打开url:', url)
                    getCurrentTabId(tabId => {
                        console.log('打开Meta页面:', meta_range_array, meta_range_array[1].range)
                        chrome.tabs.update(tabId, {url: url})
                    })
                  
                } else {
                    alert('解析完毕')
                    sendMessageToBackground({msg: MSG_ID.MSG_SET_CURRENT_MODE, payload: MODE_ID.MODE_NONE})
                }
            }
        };
        break;
        case POP_MSG_ID.MSG_UPDATE_INFO_TEXT: {
            var mode = request.payload.mode
            var text = request.payload.text
            if (mode == MODE_ID.MODE_META_BY_CLASS_ALL) {
                $('#meta_info').text(text)
            } else if (mode == MODE_ID.MODE_TIER_LIST) {
                $('#tier_info').text(text)
            } else if (mode == MODE_ID.MODE_RANK) {
                $('#rank_info').text(text)
            } else if (mode == MODE_ID.MODE_DECKS) {
                $('#deck_info').text(text)
            }
        };
        break;
        default: {
            console.log('未知消息', request.msg)
        }
    }
});

function sendMessageToBackground(message, callback) {
	chrome.runtime.sendMessage(message, function(response) {
        // console.log('收到background或者popup回复：', response);
        if(callback) callback(response)
	});
}

// 获取当前选项卡ID
function getCurrentTabId(callback)
{
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs)
	{
		if(callback) callback(tabs.length ? tabs[0].id: null);
	});
}

// 向content-script主动发送消息
function sendMessageToContentScript(message, callback)
{
	getCurrentTabId((tabId) =>
	{
		chrome.tabs.sendMessage(tabId, message, function(response)
		{
			if(callback) callback(response);
		});
	});
}
$('#clear_cache').click(() => {
    var bg = chrome.extension.getBackgroundPage()
    bg.clearAllCache()
})

$('input[name="time_range"]').click(() => {
    var objs = $("input[name='time_range']")
    console.log('aaa', objs, objs[0].checked, objs[1].checked, objs[2].checked, objs[2].value)
    for (let i in objs) {
        if (objs[i].checked) {
            localStorage['time_frame']=time_range_array[i]
        }
    }
})