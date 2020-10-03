from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(['scrapy', 'crawl', 'HearthStone'])
# execute(['scrapy', 'crawl', 'HSReport'])
# execute(['scrapy', 'crawl', 'HSRanking'])

# execute(['scrapy', 'crawl', 'HSDecks'])
# execute(['scrapy', 'crawl', 'HSDecks', '-a', "params=trending"])

# execute(['scrapy', 'crawl', 'HSDecks', '-a', "params=interrupt"])
# execute(['scrapy', 'crawl', 'HSDecks', '-a', "params=page", '-a', "page=3"])
# execute(['scrapy', 'crawl', 'HSDecks', '-a', 'rankRange=DIAMOND_THROUGH_LEGEND'])

# execute(['scrapy', 'crawl', 'HSWildDecks'])

# execute(['scrapy', 'crawl', 'BestDeck'])
# execute(['scrapy', 'crawl', 'HSWinRate'])
# execute(['scrapy', 'crawl', 'HSWinRate', '-a', 'rankRangeParams=ALL'])
# execute(['scrapy', 'crawl', 'HSWinRate', '-a', 'rankRangeParams=VIP'])
# execute(['scrapy', 'crawl', 'HSWinRate', '-a', 'rankRangeParams=TOP_1000_LEGEND'])
# execute(['scrapy', 'crawl', 'HSWinRate', '-a', 'rankRangeParams=LEGEND'])
# execute(['scrapy', 'crawl', 'HSWinRate', '-a', 'rankRangeParams=DIAMOND_THROUGH_LEGEND'])
# execute(['scrapy', 'crawl', 'HSWinRate', '-a', 'rankRangeParams=DIAMOND_FOUR_THROUGH_DIAMOND_ONE'])

# execute(['scrapy', 'crawl', 'HSWinRate', '-a', "archetype=Tortollan Mage"])

# execute(['scrapy', 'crawl', 'HSWinRate', '-a', "faction=['DemonHunter']"])
# execute(['scrapy', 'crawl', 'BestDeck', '-a', "faction=['Warrior']"])
#
# execute(['scrapy', 'crawl', 'HSArchetype'])
# execute(['scrapy', 'crawl', 'HSArchetype', '-a', 'rankRangeParams=ALL'])
# execute(['scrapy', 'crawl', 'HSArchetype', '-a', 'rankRangeParams=VIP'])
# execute(['scrapy', 'crawl', 'HSArchetype', '-a', 'rankRangeParams=TOP_1000_LEGEND'])
# execute(['scrapy', 'crawl', 'HSArchetype', '-a', 'rankRangeParams=LEGEND'])
# execute(['scrapy', 'crawl', 'HSArchetype', '-a', 'rankRangeParams=DIAMOND_THROUGH_LEGEND'])
# execute(['scrapy', 'crawl', 'HSArchetype', '-a', 'rankRangeParams=DIAMOND_FOUR_THROUGH_DIAMOND_ONE'])

# execute(['scrapy', 'crawlall'])
# execute(['scrapy', 'crawl', 'HSArenaCards', '-a', "params=extra_data"])
# execute(['scrapy', 'crawl', 'HSArenaCards', '-a', "card_hsid=54264"])

# execute(['scrapy', 'crawl', 'HSBattlegrounds'])
execute(['scrapy', 'crawl', 'HSArenaCards', '-a', 'local_update=True'])